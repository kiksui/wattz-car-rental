import traceback
from telegram import Update
from telegram.ext import ContextTypes
from .logger import get_logger

logger = get_logger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {update}</pre>\n\n"
        f"<pre>{tb_string}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=context.bot_data.get("developer_chat_id", "YOUR_DEVELOPER_CHAT_ID"),
        text=message,
        parse_mode='HTML'
    )

    # If the error is in a callback query, we need to answer it to avoid a timeout
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.answer(
            text="An error occurred. The developer has been notified.",
            show_alert=True
        )