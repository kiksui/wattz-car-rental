import pytest
from unittest.mock import AsyncMock, patch
from handlers import message_handler, callback_handler

@pytest.mark.asyncio
async def test_handle_message():
    update = AsyncMock()
    context = AsyncMock()
    await message_handler.handle_message(update, context)
    update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_handle_callback():
    update = AsyncMock()
    context = AsyncMock()
    update.callback_query.data = 'test_callback'
    with patch('handlers.callback_handler.handle_booking_callback', new_callable=AsyncMock) as mock_handle_booking:
        await callback_handler.handle_callback(update, context)
        mock_handle_booking.assert_called_once()