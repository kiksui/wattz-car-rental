from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MINI_APP_URL
from services.user_service import get_user_kyc_status

async def kyc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kyc_url = f"{MINI_APP_URL}/kyc?user_id={user.id}"
    
    keyboard = [
        [InlineKeyboardButton("Start KYC Process", web_app={"url": kyc_url})],
        [InlineKeyboardButton("Check KYC Status", callback_data="check_kyc_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hello {user.first_name}! To rent a car, we need to verify your identity.\n\n"
        "Our KYC process is quick, easy, and secure. Just click the button below to get started!\n\n"
        "You'll need to provide the following:\n"
        "1. Your personal information\n"
        "2. A clear photo of your ID\n"
        "3. A clear photo of your driving license\n"
        "4. A selfie of you holding your ID",
        reply_markup=reply_markup
    )

async def check_kyc_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kyc_status = await get_user_kyc_status(user.id)
    
    if kyc_status == "approved":
        message = "Great news! Your KYC is approved. You can now rent cars with Wattz Car Rental."
    elif kyc_status == "pending":
        message = "Your KYC is still under review. We'll notify you once it's approved."
    elif kyc_status == "rejected":
        message = "Unfortunately, your KYC was not approved. Please contact our support for more information."
    else:
        message = "You haven't completed the KYC process yet. Use the /kyc command to get started!"
    
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(message)