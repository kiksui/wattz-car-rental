import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from commands import start, help, book, kyc, calendar, booking_status, booking_manage, admin, cancel, goodbye
from handlers import message_handler, callback_handler
from utils.error_handler import error_handler
from utils.logger import get_logger
from utils.database import connect_to_database
from services import booking_service, payment_service

# Load environment variables
load_dotenv()

# Set up logging
logger = get_logger(__name__)

async def handle_payment_callback(update, context):
    callback_data = update.callback_query.data
    _, status, booking_id = callback_data.split('_')
    if status == 'success':
        try:
            booking = await booking_service.get_booking(booking_id)
            await payment_service.verify_payment(booking['payment_session_id'])
            await update.callback_query.message.reply_text("Thank you! Your payment has been confirmed and your booking is now complete.")
        except (booking_service.BookingError, payment_service.PaymentError) as e:
            logger.error(f"Payment verification failed: {str(e)}")
            await update.callback_query.message.reply_text("There was an issue confirming your payment. Please contact customer support.")
    elif status == 'cancel':
        await update.callback_query.message.reply_text("Your payment was cancelled. If you'd like to try again, please use the /book command.")

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    # Connect to database
    connect_to_database()

    # Command handlers
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", help.help_command))
    application.add_handler(CommandHandler("book", book.book_command))
    application.add_handler(CommandHandler("kyc", kyc.kyc_command))
    application.add_handler(CommandHandler("calendar", calendar.calendar_command))
    application.add_handler(CommandHandler("bookingstatus", booking_status.booking_status_command))
    application.add_handler(CommandHandler("bookingmanage", booking_manage.booking_manage_command))
    application.add_handler(CommandHandler("admin", admin.admin_command))
    application.add_handler(CommandHandler("cancel", cancel.cancel_command))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_message))

    # Callback query handler
    application.add_handler(callback_handler.callback_handler)

    # Specific callback handlers
    application.add_handler(callback_handler.CallbackQueryHandler(goodbye.goodbye_command, pattern="^goodbye$"))
    application.add_handler(callback_handler.CallbackQueryHandler(goodbye.end_conversation, pattern="^end_conversation$"))
    application.add_handler(callback_handler.CallbackQueryHandler(start.start_command, pattern="^start$"))
    application.add_handler(callback_handler.CallbackQueryHandler(handle_payment_callback, pattern="^payment_"))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()

    logger.info("Bot started successfully!")

if __name__ == '__main__':
    main()