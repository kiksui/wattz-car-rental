# bot/handlers/calendar_handler.py

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from commands.calendar import show_month_calendar
from datetime import datetime, timedelta
from services.calendar_service import check_date_range_availability

async def handle_calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    
    if data.startswith("cal_prev_") or data.startswith("cal_next_"):
        year, month = map(int, data.split("_")[2].split("-"))
        if data.startswith("cal_prev_"):
            base_date = datetime(year, month, 1) - timedelta(days=1)
        else:
            base_date = datetime(year, month, 1) + timedelta(days=32)
        base_date = base_date.replace(day=1)
        await show_month_calendar(update, context, base_date)
    
    elif data.startswith("date_"):
        selected_date = datetime.strptime(data.split("_")[1], "%Y-%m-%d").date()
        context.user_data['selected_date'] = selected_date
        
        # If this is the first date selected, ask for the end date
        if 'start_date' not in context.user_data:
            context.user_data['start_date'] = selected_date
            await query.edit_message_text(f"Start date selected: {selected_date}. Please select an end date.")
            await show_month_calendar(update, context, selected_date)
        else:
            # This is the end date
            start_date = context.user_data['start_date']
            end_date = selected_date
            
            # Ensure start_date is before end_date
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            
            # Check availability for the selected date range
            is_available = await check_date_range_availability(start_date, end_date)
            
            if is_available:
                await query.edit_message_text(
                    f"Date range selected: {start_date} to {end_date}. "
                    f"This range is available. Would you like to proceed with booking?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Proceed to Booking", callback_data="proceed_booking")],
                        [InlineKeyboardButton("Cancel", callback_data="cancel_booking")]
                    ])
                )
            else:
                await query.edit_message_text(
                    f"Sorry, the selected date range ({start_date} to {end_date}) is not fully available. "
                    f"Please select a different range.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Try Again", callback_data="show_calendar")],
                        [InlineKeyboardButton("Cancel", callback_data="cancel_booking")]
                    ])
                )
            
            # Clear the selected dates
            context.user_data.pop('start_date', None)
            context.user_data.pop('selected_date', None)

calendar_handler = CallbackQueryHandler(handle_calendar_callback, pattern=r"^(cal_|date_)")