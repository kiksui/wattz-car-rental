# bot/commands/booking_manage.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.booking_service import get_user_bookings

async def booking_manage_command(update, context):
    user_id = update.effective_user.id
    bookings = await get_user_bookings(user_id)
    
    if not bookings:
        await update.message.reply_text("You don't have any active bookings to manage.")
        return

    keyboard = []
    for booking in bookings:
        keyboard.append([InlineKeyboardButton(
            f"Manage Booking {booking['_id']}",
            callback_data=f"manage_{booking['_id']}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a booking to manage:", reply_markup=reply_markup)