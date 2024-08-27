# bot/commands/calendar.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.calendar_service import get_available_dates
from datetime import datetime, timedelta

async def calendar_command(update, context: ContextTypes.DEFAULT_TYPE):
    await show_month_calendar(update, context)

async def show_month_calendar(update, context: ContextTypes.DEFAULT_TYPE, base_date=None):
    if not base_date:
        base_date = datetime.now().date().replace(day=1)

    available_dates = await get_available_dates(base_date, base_date + timedelta(days=31))
    
    calendar_keyboard = []
    week = []
    
    # Add month navigation
    calendar_keyboard.append([
        InlineKeyboardButton("<<", callback_data=f"cal_prev_{base_date.strftime('%Y-%m')}"),
        InlineKeyboardButton(f"{base_date.strftime('%B %Y')}", callback_data="ignore"),
        InlineKeyboardButton(">>", callback_data=f"cal_next_{base_date.strftime('%Y-%m')}")
    ])
    
    # Add weekday headers
    calendar_keyboard.append(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])
    
    # Fill in the dates
    for i in range(42):  # 6 weeks * 7 days
        current_date = base_date + timedelta(days=i)
        if i > 0 and i % 7 == 0:
            calendar_keyboard.append(week)
            week = []
        
        if current_date.month != base_date.month:
            week.append(" ")
        else:
            date_str = current_date.strftime("%d")
            if current_date in available_dates:
                callback_data = f"date_{current_date.strftime('%Y-%m-%d')}"
                week.append(InlineKeyboardButton(date_str, callback_data=callback_data))
            else:
                week.append(date_str)
    
    if week:
        calendar_keyboard.append(week)
    
    reply_markup = InlineKeyboardMarkup(calendar_keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text("Please select a date:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please select a date:", reply_markup=reply_markup)