# bot/commands/book.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from services.car_service import get_available_car_types
from services.booking_service import create_booking
from services.payment_service import create_payment_link, PaymentError
from utils.logger import get_logger

logger = get_logger(__name__)

# Define conversation states
SELECTING_CAR, SELECTING_DATES, CONFIRMING_BOOKING = range(3)

async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_booking(update, context)
    return SELECTING_CAR

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    car_types = await get_available_car_types()
    
    keyboard = [
        [InlineKeyboardButton(car_type, callback_data=f"car_type_{car_type}")]
        for car_type in car_types
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Please select a car type:", reply_markup=reply_markup)

async def car_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    car_type = query.data.split("_")[2]
    context.user_data['car_type'] = car_type
    
    await query.edit_message_text(f"You've selected {car_type}. Now, let's choose your rental dates.")
    # Here you would call your calendar function to let the user select dates
    # For this example, we'll just move to the next state
    return SELECTING_DATES

async def dates_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In a real scenario, you would get these dates from user input
    context.user_data['start_date'] = "2023-06-01"
    context.user_data['end_date'] = "2023-06-05"
    
    car_type = context.user_data['car_type']
    start_date = context.user_data['start_date']
    end_date = context.user_data['end_date']
    
    keyboard = [
        [InlineKeyboardButton("Confirm Booking", callback_data="confirm_booking")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_booking")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Please confirm your booking:\n"
        f"Car Type: {car_type}\n"
        f"Start Date: {start_date}\n"
        f"End Date: {end_date}",
        reply_markup=reply_markup
    )
    return CONFIRMING_BOOKING

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    car_type = context.user_data['car_type']
    start_date = context.user_data['start_date']
    end_date = context.user_data['end_date']
    
    try:
        booking = await create_booking(user_id, car_type, start_date, end_date)
        payment_link = await create_payment_link(booking['_id'])
        
        keyboard = [[InlineKeyboardButton("Pay Now", url=payment_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Great! Your booking is confirmed. Please complete the payment to finalize.\n\n"
            f"Booking details:\n"
            f"Booking ID: {booking['_id']}\n"
            f"Car Type: {car_type}\n"
            f"Start Date: {start_date}\n"
            f"End Date: {end_date}\n"
            f"Total Price: ${booking['total_price']:.2f}\n\n"
            f"Click the button below to proceed to payment:",
            reply_markup=reply_markup
        )
    except PaymentError as e:
        logger.error(f"Payment error for user {user_id}: {str(e)}")
        await query.edit_message_text(
            "We're sorry, but there was an error processing your payment. Please try again later or contact support."
        )
    except Exception as e:
        logger.error(f"Unexpected error in confirm_booking for user {user_id}: {str(e)}")
        await query.edit_message_text(
            "An unexpected error occurred. Please try again later or contact support."
        )
    
    return ConversationHandler.END

async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("Booking cancelled. Feel free to start a new booking when you're ready.")
    return ConversationHandler.END

book_conversation = ConversationHandler(
    entry_points=[CommandHandler('book', book_command)],
    states={
        SELECTING_CAR: [CallbackQueryHandler(car_type_selected, pattern=r"^car_type_")],
        SELECTING_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, dates_selected)],
        CONFIRMING_BOOKING: [
            CallbackQueryHandler(confirm_booking, pattern="^confirm_booking$"),
            CallbackQueryHandler(cancel_booking, pattern="^cancel_booking$")
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_booking)]
)