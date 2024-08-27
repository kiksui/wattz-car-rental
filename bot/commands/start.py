from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mini_app_url = "https://t.me/your_mini_app"  # Replace with your actual mini app URL
    
    keyboard = [
        [InlineKeyboardButton("Open Mini App", web_app={"url": mini_app_url})],
        [InlineKeyboardButton("Book a Car", callback_data="book_car")],
        [InlineKeyboardButton("Complete KYC", callback_data="start_kyc")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome, {user.first_name}! I'm your car rental assistant. "
        "You can use our mini app for a seamless experience or use the bot commands.",
        reply_markup=reply_markup
    )

# Keep the original help functionality
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = """
Available commands:
/start - Start the bot
/help - Show this help message
/book - Book a car
/kyc - Complete KYC process
/status - Check your current booking status
/cancel - Cancel your current booking
/contact - Get in touch with customer support

Need more assistance? Just ask!
    """
    await update.message.reply_text(help_message)