# bot/commands/admin.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.admin_service import is_admin

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("You don't have permission to access admin commands.")
        return

    keyboard = [
        [InlineKeyboardButton("Manage Cars", callback_data="admin_manage_cars")],
        [InlineKeyboardButton("Manage Bookings", callback_data="admin_manage_bookings")],
        [InlineKeyboardButton("Generate Reports", callback_data="admin_generate_reports")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Portal. Choose an action:", reply_markup=reply_markup)

async def manage_cars_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("Add Car", callback_data="admin_add_car")],
        [InlineKeyboardButton("Remove Car", callback_data="admin_remove_car")],
        [InlineKeyboardButton("Update Car", callback_data="admin_update_car")],
        [InlineKeyboardButton("List Cars", callback_data="admin_list_cars")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Car Management. Choose an action:", reply_markup=reply_markup)

async def manage_bookings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("View All Bookings", callback_data="admin_view_bookings")],
        [InlineKeyboardButton("Cancel Booking", callback_data="admin_cancel_booking")],
        [InlineKeyboardButton("Modify Booking", callback_data="admin_modify_booking")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Booking Management. Choose an action:", reply_markup=reply_markup)

async def generate_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("Revenue Report", callback_data="admin_revenue_report")],
        [InlineKeyboardButton("Booking Statistics", callback_data="admin_booking_stats")],
        [InlineKeyboardButton("Car Utilization Report", callback_data="admin_car_utilization")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Report Generation. Choose a report:", reply_markup=reply_markup)