import pytest
from unittest.mock import patch, MagicMock
from services import booking_service, payment_service

@pytest.mark.asyncio
async def test_create_booking():
    with patch('services.booking_service.connect_to_database', return_value=MagicMock()):
        result = await booking_service.create_booking('user123', 'car456', '2023-06-01', '2023-06-05', 'New York', 'Boston')
        assert result['status'] == 'pending'

@pytest.mark.asyncio
async def test_cancel_booking():
    with patch('services.booking_service.connect_to_database', return_value=MagicMock()):
        result = await booking_service.cancel_booking('booking789')
        assert result is True

@pytest.mark.asyncio
async def test_initiate_payment():
    with patch('services.payment_service.stripe.checkout.Session.create', return_value=MagicMock(url='https://payment.url')):
        result = await payment_service.initiate_payment('booking123', 100.00)
        assert 'https://payment.url' in result