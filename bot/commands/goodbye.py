from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def goodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Return to Main Menu", callback_data="start")],
        [InlineKeyboardButton("End Conversation", callback_data="end_conversation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Thank you for using Wattz Car Rental. Is there anything else I can help you with?",
        reply_markup=reply_markup
    )

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Thank you for using Wattz Car Rental. Have a great day! If you need assistance in the future, just send /start to begin a new conversation."
    )