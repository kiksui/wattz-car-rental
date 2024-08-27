# bot/handlers/miniapp_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from services.booking_service import confirm_booking
from services.kyc_service import update_kyc_status

async def handle_miniapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.effective_message.web_app_data.data
    user_id = update.effective_user.id

    if data.startswith("booking:"):
        await handle_booking_data(user_id, data)
    elif data.startswith("kyc:"):
        await handle_kyc_data(user_id, data)
    else:
        await update.message.reply_text("Invalid data received from mini app.")

async def handle_booking_data(user_id: int, data: str):
    # Extract booking details from data
    booking_details = data.split(":")[1]
    # Process the booking
    booking = await confirm_booking(user_id, booking_details)
    # Send confirmation message
    await context.bot.send_message(
        user_id,
        f"Booking confirmed! Your booking ID is {booking['id']}. "
        f"Total price: ${booking['total_price']:.2f}"
    )

async def handle_kyc_data(user_id: int, data: str):
    # Extract KYC status from data
    kyc_status = data.split(":")[1]
    # Update KYC status
    await update_kyc_status(user_id, kyc_status)
    # Send confirmation message
    await context.bot.send_message(
        user_id,
        "Your KYC information has been successfully updated."
    )