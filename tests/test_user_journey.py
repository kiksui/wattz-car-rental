import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update
from commands import start, book, kyc
from services import booking_service, payment_service
from app import app

@pytest.mark.asyncio
async def test_complete_user_journey():
    # Simulate starting the bot
    update = AsyncMock()
    context = AsyncMock()
    await start.start_command(update, context)
    
    # Simulate booking process
    with patch('commands.book.create_booking', new_callable=AsyncMock) as mock_create_booking:
        mock_create_booking.return_value = {'id': 'booking123'}
        await book.book_command(update, context)
    
    # Simulate payment process
    with patch('services.payment_service.initiate_payment', new_callable=AsyncMock) as mock_initiate_payment:
        mock_initiate_payment.return_value = 'https://payment.url'
        payment_url = await payment_service.initiate_payment('booking123', 100.00)
        assert 'https://payment.url' in payment_url
    
    # Simulate KYC process
    await kyc.kyc_command(update, context)
    
    # Test mini app KYC submission
    with app.test_client() as client:
        kyc_data = {
            'user_id': 'user123',
            'full_name': 'John Doe',
            'date_of_birth': '1990-01-01',
            'nationality': 'US',
            'id_type': 'passport',
            'id_number': 'AB1234567'
        }
        response = client.post('/api/kyc', json=kyc_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    # Verify booking status
    with patch('services.booking_service.get_booking', new_callable=AsyncMock) as mock_get_booking:
        mock_get_booking.return_value = {'status': 'confirmed'}
        booking = await booking_service.get_booking('booking123')
        assert booking['status'] == 'confirmed'

    print("End-to-end test completed successfully!")