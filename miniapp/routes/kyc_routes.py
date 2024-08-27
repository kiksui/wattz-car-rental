import os
from flask import Blueprint, jsonify, request
from models.user import User
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL
from utils.logger import kyc_logger
from database import db
from werkzeug.utils import secure_filename

kyc_routes = Blueprint('kyc_routes', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@kyc_routes.route('/kyc', methods=['POST'])
def submit_kyc():
    try:
        user_id = request.form.get('user_id')
        user = User.find_one({"user_id": user_id})
        
        if not user:
            user = User(user_id=user_id)
        
        user.full_name = request.form.get('fullName')
        user.date_of_birth = request.form.get('dateOfBirth')
        user.nationality = request.form.get('nationality')
        user.id_type = request.form.get('idType')
        user.id_number = request.form.get('idNumber')
        user.kyc_status = 'pending'

        # Handle file uploads
        id_photo = request.files.get('idPhoto')
        driving_license = request.files.get('drivingLicense')
        selfie = request.files.get('selfie')

        if id_photo and allowed_file(id_photo.filename):
            filename = secure_filename(f"{user_id}_id.{id_photo.filename.rsplit('.', 1)[1].lower()}")
            id_photo.save(os.path.join(UPLOAD_FOLDER, filename))
            user.id_photo_path = filename

        if driving_license and allowed_file(driving_license.filename):
            filename = secure_filename(f"{user_id}_license.{driving_license.filename.rsplit('.', 1)[1].lower()}")
            driving_license.save(os.path.join(UPLOAD_FOLDER, filename))
            user.driving_license_path = filename

        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(f"{user_id}_selfie.{selfie.filename.rsplit('.', 1)[1].lower()}")
            selfie.save(os.path.join(UPLOAD_FOLDER, filename))
            user.selfie_path = filename
        
        db.users.update_one({"user_id": user.user_id}, {"$set": user.__dict__}, upsert=True)
        
        # Send KYC data to Telegram bot
        kyc_details = f"{user.user_id}:{user.full_name}:{user.kyc_status}"
        payload = {
            'chat_id': user.user_id,
            'text': f"KYC submitted:\n{kyc_details}\nOur team will review your information shortly."
        }
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
        if response.status_code == 200:
            kyc_logger.info(f"KYC submitted and sent to Telegram bot. User ID: {user.user_id}")
            return jsonify({"status": "success", "message": "KYC submitted and sent to Telegram bot"}), 200
        else:
            kyc_logger.warning(f"KYC submitted but failed to send to Telegram bot. User ID: {user.user_id}")
            return jsonify({"status": "warning", "message": "KYC submitted but failed to send to Telegram bot"}), 200
    except Exception as e:
        kyc_logger.error(f"Error submitting KYC: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while submitting KYC"}), 500

@kyc_routes.route('/kyc/<int:user_id>', methods=['GET'])
def get_kyc_status(user_id):
    try:
        user = User.find_one({"user_id": user_id})
        if user:
            kyc_logger.info(f"KYC status retrieved. User ID: {user_id}")
            return jsonify({"kyc_status": user.kyc_status})
        else:
            return jsonify({"kyc_status": "not_found"})
    except Exception as e:
        kyc_logger.error(f"Error retrieving KYC status for user {user_id}: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while retrieving KYC status"}), 500

@kyc_routes.route('/admin/kyc', methods=['GET'])
def admin_get_all_kyc():
    try:
        # Add authentication check here to ensure only admin can access this route
        users = list(db.users.find({}, {"_id": 0}))
        return jsonify({"status": "success", "data": users})
    except Exception as e:
        kyc_logger.error(f"Error retrieving all KYC data: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while retrieving KYC data"}), 500

@kyc_routes.route('/admin/kyc/<int:user_id>', methods=['PUT'])
def admin_update_kyc_status(user_id):
    try:
        # Add authentication check here to ensure only admin can access this route
        data = request.json
        new_status = data.get('kyc_status')
        if new_status not in ['approved', 'rejected', 'pending']:
            return jsonify({"status": "error", "message": "Invalid KYC status"}), 400
        
        result = db.users.update_one({"user_id": user_id}, {"$set": {"kyc_status": new_status}})
        if result.modified_count > 0:
            return jsonify({"status": "success", "message": f"KYC status updated to {new_status}"})
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        kyc_logger.error(f"Error updating KYC status for user {user_id}: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while updating KYC status"}), 500