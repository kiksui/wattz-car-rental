import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_available_cars(client):
    response = client.get('/api/car')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_create_booking(client):
    booking_data = {
        'user_id': 'user123',
        'car_id': 'car456',
        'pickup_date': '2023-06-01',
        'return_date': '2023-06-05',
        'pickup_location': 'New York',
        'return_location': 'Boston'
    }
    response = client.post('/api/booking/create', json=booking_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'booking_id' in data

def test_submit_kyc(client):
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
    data = json.loads(response.data)
    assert data['status'] == 'success'