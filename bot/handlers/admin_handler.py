# bot/handlers/admin_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.admin_service import (
    add_car, remove_car, update_car, list_cars,
    view_all_bookings, cancel_booking, modify_booking,
    generate_revenue_report, generate_booking_stats, generate_car_utilization_report
)

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_manage_cars":
        await handle_manage_cars(update, context)
    elif query.data == "admin_manage_bookings":
        await handle_manage_bookings(update, context)
    elif query.data == "admin_generate_reports":
        await handle_generate_reports(update, context)
    elif query.data == "admin_add_car":
        context.user_data['admin_state'] = 'add_car'
        await query.edit_message_text("Please enter the car details in this format: Brand, Model, Year, Type, Daily Rate")
    elif query.data == "admin_remove_car":
        cars = await list_cars()
        keyboard = [[InlineKeyboardButton(f"{car['brand']} {car['model']} ({car['year']})", callback_data=f"remove_car_{car['_id']}")] for car in cars]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a car to remove:", reply_markup=reply_markup)
    elif query.data.startswith("remove_car_"):
        car_id = query.data.split("_")[2]
        await remove_car(car_id)
        await query.edit_message_text("Car removed successfully.")
    # Add more handlers for other admin actions...

async def handle_manage_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementation for managing cars...

async def handle_manage_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementation for managing bookings...

async def handle_generate_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Implementation for generating reports...

admin_handler = CallbackQueryHandler(handle_admin_callback, pattern=r"^admin_")