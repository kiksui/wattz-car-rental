# bot/services/payment_service.py

import os
from dotenv import load_dotenv
import stripe
from services.booking_service import get_booking, update_booking_status
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

class PaymentError(Exception):
    pass

async def initiate_payment(booking_id, total_price):
    try:
        booking = await get_booking(booking_id)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Car Rental - Booking ID: {booking_id}',
                        'description': f'From {booking["start_date"]} to {booking["end_date"]}'
                    },
                    'unit_amount': int(total_price * 100),  # Stripe uses cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://t.me/YourBot?start=payment_success_{booking_id}',
            cancel_url=f'https://t.me/YourBot?start=payment_cancel_{booking_id}',
            client_reference_id=str(booking_id)
        )

        # Store the session ID with the booking for later verification
        await update_booking_status(booking_id, 'payment_pending', {'payment_session_id': session.id})

        return session.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error initiating payment: {str(e)}")
        raise PaymentError(f"Failed to initiate payment: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error initiating payment: {str(e)}")
        raise PaymentError("An unexpected error occurred while initiating the payment")

async def verify_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            booking_id = session.client_reference_id
            await update_booking_status(booking_id, 'confirmed', {'payment_intent_id': session.payment_intent})
            return True
        return False
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error verifying payment: {str(e)}")
        raise PaymentError(f"Failed to verify payment: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error verifying payment: {str(e)}")
        raise PaymentError("An unexpected error occurred while verifying the payment")

async def process_refund(booking_id):
    try:
        booking = await get_booking(booking_id)
        refund = stripe.Refund.create(
            payment_intent=booking['payment_intent_id'],
            amount=int(booking['total_price'] * 100)  # Refund in cents
        )
        if refund.status == 'succeeded':
            await update_booking_status(booking_id, 'refunded')
            return True
        return False
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error processing refund: {str(e)}")
        raise PaymentError(f"Failed to process refund: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing refund: {str(e)}")
        raise PaymentError("An unexpected error occurred while processing the refund")

async def handle_stripe_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload in Stripe webhook: {str(e)}")
        raise PaymentError('Invalid payload')
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature in Stripe webhook: {str(e)}")
        raise PaymentError('Invalid signature')

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await verify_payment(session.id)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')
        if booking_id:
            await update_booking_status(booking_id, 'payment_failed')

    # Handle other event types as needed

    return True