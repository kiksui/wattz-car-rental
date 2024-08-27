# bot/commands/booking_status.py

from services.booking_service import get_user_bookings

async def booking_status_command(update, context):
    user_id = update.effective_user.id
    bookings = await get_user_bookings(user_id)
    
    if not bookings:
        await update.message.reply_text("You don't have any active bookings.")
        return

    status_message = "Your current bookings:\n\n"
    for booking in bookings:
        status_message += f"Booking ID: {booking['_id']}\n"
        status_message += f"Car Type: {booking['car_type']}\n"
        status_message += f"Pickup Date: {booking['pickup_date']}\n"
        status_message += f"Return Date: {booking['return_date']}\n"
        status_message += f"Status: {booking['status']}\n\n"

    await update.message.reply_text(status_message)