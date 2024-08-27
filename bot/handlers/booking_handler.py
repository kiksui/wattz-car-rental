# bot/handlers/booking_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.booking_service import create_booking, get_booking, cancel_booking
from services.payment_service import create_payment_link, PaymentError
from utils.logger import get_logger

logger = get_logger(__name__)

async def handle_booking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "proceed_booking":
        await handle_proceed_booking(update, context)
    elif query.data == "cancel_booking":
        await handle_cancel_booking(update, context)
    elif query.data.startswith("pay_booking_"):
        await handle_payment(update, context)

async def handle_proceed_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    car_type = context.user_data.get('car_type')
    start_date = context.user_data.get('start_date')
    end_date = context.user_data.get('end_date')
    pickup_location = context.user_data.get('pickup_location')
    dropoff_location = context.user_data.get('dropoff_location')

    try:
        booking = await create_booking(user_id, car_type, start_date, end_date, pickup_location, dropoff_location)
        payment_link = await create_payment_link(booking['_id'])
        
        keyboard = [[InlineKeyboardButton("Pay Now", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"Great! Your booking is created. Please complete the payment to confirm.\n\n"
            f"Booking details:\n"
            f"Car Type: {car_type}\n"
            f"Start Date: {start_date}\n"
            f"End Date: {end_date}\n"
            f"Total Price: ${booking['total_price']:.2f}\n\n"
            f"Click the button below to proceed to payment:",
            reply_markup=reply_markup
        )
    except PaymentError as e:
        logger.error(f"Payment error for user {user_id}: {str(e)}")
        await update.callback_query.edit_message_text(
            "We're sorry, but there was an error processing your payment. Please try again later or contact support."
        )
    except Exception as e:
        logger.error(f"Unexpected error in handle_proceed_booking for user {user_id}: {str(e)}")
        await update.callback_query.edit_message_text(
            "An unexpected error occurred. Please try again later or contact support."
        )

async def handle_cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    booking_id = context.user_data.get('current_booking_id')
    
    if booking_id:
        try:
            await cancel_booking(booking_id)
            await update.callback_query.edit_message_text("Your booking has been cancelled.")
        except Exception as e:
            logger.error(f"Error cancelling booking {booking_id} for user {user_id}: {str(e)}")
            await update.callback_query.edit_message_text("There was an error cancelling your booking. Please try again or contact support.")
    else:
        await update.callback_query.edit_message_text("No active booking found to cancel.")

    context.user_data.clear()

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    booking_id = query.data.split("_")[2]
    
    try:
        booking = await get_booking(booking_id)
        payment_link = await create_payment_link(booking_id)
        
        keyboard = [[InlineKeyboardButton("Pay Now", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Ready to complete your payment for booking {booking_id}?\n\n"
            f"Total Amount: ${booking['total_price']:.2f}\n\n"
            f"Click the button below to proceed to payment:",
            reply_markup=reply_markup
        )
    except PaymentError as e:
        logger.error(f"Payment error for booking {booking_id}: {str(e)}")
        await query.edit_message_text(
            "We're sorry, but there was an error processing your payment. Please try again later or contact support."
        )
    except Exception as e:
        logger.error(f"Unexpected error in handle_payment for booking {booking_id}: {str(e)}")
        await query.edit_message_text(
            "An unexpected error occurred. Please try again later or contact support."
        )

booking_handler = CallbackQueryHandler(handle_booking_callback, pattern=r"^(proceed_booking|cancel_booking|pay_booking_)")