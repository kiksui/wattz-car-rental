# bot/commands/help.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def help_command(update, context):
    help_message = """
Available commands:
/start - Start the bot
/help - Show this help message
/book - Book a car
/kyc - Complete KYC process
/calendar - Check car availability
/bookingstatus - Check your current booking status
/bookingmanage - Manage your current booking
/admin - Admin commands (for authorized users only)

Need more assistance? Just ask!
    """
    keyboard = [
        [InlineKeyboardButton("Book a Car", callback_data="book")],