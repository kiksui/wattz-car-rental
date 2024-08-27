from database import db
from utils.logger import user_logger

async def get_user_kyc_status(user_id):
    try:
        user = await db.users.find_one({"user_id": user_id})
        if user:
            return user.get('kyc_status', 'not_submitted')
        return 'not_submitted'
    except Exception as e:
        user_logger.error(f"Error getting KYC status for user {user_id}: {str(e)}")
        return 'error'

async def update_user_kyc_status(user_id, new_status):
    try:
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"kyc_status": new_status}}
        )
        if result.modified_count > 0:
            user_logger.info(f"KYC status updated for user {user_id}: {new_status}")
            return True
        else:
            user_logger.warning(f"No KYC status update for user {user_id}: User not found or status unchanged")
            return False
    except Exception as e:
        user_logger.error(f"Error updating KYC status for user {user_id}: {str(e)}")
        return False