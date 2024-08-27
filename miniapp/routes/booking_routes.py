from flask import Blueprint, jsonify, request
from models.car import Car
from models.booking import Booking
from services.booking_service import check_car_availability, create_booking
from services.payment_service import initiate_payment
from utils.logger import get_logger
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL
from datetime import datetime

booking_routes = Blueprint('booking_routes', __name__)
logger = get_logger(__name__)

@booking_routes.route('/cars', methods=['GET'])
def get_available_cars():
    try:
        cars = Car.query.filter_by(status='available').all()
        return jsonify([car.to_dict() for car in cars])
    except Exception as e:
        logger.error(f"Error fetching available cars: {str(e)}")
        return jsonify({"status": "error", "message": "Unable to fetch available cars"}), 500

@booking_routes.route('/booking/create', methods=['POST'])
def create_new_booking():
    try:
        data = request.json
        car_id = data['car_id']
        pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%d')
        return_date = datetime.strptime(data['return_date'], '%Y-%m-%d')
        
        # Check car availability
        if not check_car_availability(car_id, pickup_date, return_date):
            return jsonify({"status": "error", "message": "Car is not available for the selected dates"}), 400
        
        # Create booking
        booking = create_booking(
            user_id=data['user_id'],
            car_id=car_id,
            pickup_date=pickup_date,
            return_date=return_date,
            pickup_location=data['pickup_location'],
            return_location=data['return_location']
        )
        
        # Initiate payment process
        payment_link = initiate_payment(booking.id, booking.total_price)
        
        # Send booking data to Telegram bot
        booking_details = f"{booking.id}:{car_id}:{pickup_date}:{return_date}"
        payload = {
            'chat_id': data['user_id'],
            'text': f"New booking created:\n{booking_details}\nPayment link: {payment_link}"
        }
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

        if response.status_code == 200:
            logger.info(f"Booking created and sent to Telegram bot. Booking ID: {booking.id}")
        else:
            logger.warning(f"Booking created but failed to send to Telegram bot. Booking ID: {booking.id}")

        return jsonify({
            "status": "success",
            "booking_id": booking.id,
            "payment_link": payment_link
        })
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        return jsonify({"status": "error", "message": "Unable to create booking"}), 500

@booking_routes.route('/booking/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        return jsonify(booking.to_dict())
    except Exception as e:
        logger.error(f"Error fetching booking {booking_id}: {str(e)}")
        return jsonify({"status": "error", "message": "Unable to fetch booking details"}), 500

@booking_routes.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.json

        booking.pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%d')
        booking.return_date = datetime.strptime(data['return_date'], '%Y-%m-%d')
        booking.pickup_location = data['pickup_location']
        booking.return_location = data['return_location']

        booking.save()

        # Send updated booking data to Telegram bot
        booking_details = f"{booking.id}:{booking.car_id}:{booking.pickup_date}:{booking.return_date}"
        payload = {
            'chat_id': booking.user_id,
            'text': f"Booking updated:\n{booking_details}"
        }
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

        if response.status_code == 200:
            logger.info(f"Booking updated and sent to Telegram bot. Booking ID: {booking_id}")
        else:
            logger.warning(f"Booking updated but failed to send to Telegram bot. Booking ID: {booking_id}")

        return jsonify({"status": "success", "message": "Booking updated", "booking": booking.to_dict()})
    except Exception as e:
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while updating the booking"}), 500

@booking_routes.route('/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        user_id = booking.user_id
        booking.delete()

        # Send cancellation data to Telegram bot
        payload = {
            'chat_id': user_id,
            'text': f"Booking cancelled: {booking_id}"
        }
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

        if response.status_code == 200:
            logger.info(f"Booking cancelled and notification sent to Telegram bot. Booking ID: {booking_id}")
        else:
            logger.warning(f"Booking cancelled but failed to send notification to Telegram bot. Booking ID: {booking_id}")

        return jsonify({"status": "success", "message": "Booking cancelled"}), 200
    except Exception as e:
        logger.error(f"Error cancelling booking {booking_id}: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while cancelling the booking"}), 500

@booking_routes.route('/complete_booking', methods=['POST'])
def complete_booking():
    try:
        data = request.json
        user_id = data['user_id']
        booking_id = data['booking_id']

        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'completed'
        booking.save()

        # Send data back to the Telegram bot
        payload = {
            'chat_id': user_id,
            'text': f"Booking completed: {booking_id}"
        }
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

        if response.status_code == 200:
            logger.info(f"Booking completion data sent to Telegram bot. User ID: {user_id}, Booking ID: {booking_id}")
            return jsonify({"status": "success", "message": "Booking completed"}), 200
        else:
            logger.warning(f"Failed to send booking completion data to Telegram bot. User ID: {user_id}, Booking ID: {booking_id}")
            return jsonify({"status": "warning", "message": "Booking completed but failed to notify Telegram bot"}), 200
    except Exception as e:
        logger.error(f"Error completing booking: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while completing the booking"}), 500