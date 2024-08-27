# Wattz Car Rental Bot and Mini App

This project consists of a Telegram bot and a mini app for car rental services.

## Setup

### Prerequisites
- Python 3.9+
- MongoDB
- Telegram Bot Token
- Stripe API Key (for payments)

### Installation

1. Clone the repository:https://github.com/kiksui/wattz-car-rental.git
2. Create a virtual environment and activate it:
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:
pip3 install -r requirements.txt
4. Set up environment variables:
Create a `.env` file in the root directory and add the following:

### Running the Bot

1. Start the bot:
python3 bot/bot.py

### Running the Mini App

1. Start the Flask server:
python3 miniapp/app.py

## Usage

### Bot Commands
- `/start`: Start the bot and see available options
- `/book`: Start the booking process
- `/kyc`: Complete the KYC process
- `/status`: Check booking status
- `/cancel`: Cancel a booking
- `/help`: Get help and see all available commands

### Mini App
The mini app provides a web interface for:
- Viewing available cars
- Completing the booking process
- Submitting KYC information

## Development

### Running Tests
pytest tests/

### Adding New Features
1. Create new command files in `bot/commands/`
2. Update `bot/bot.py` to include new command handlers
3. Add new routes in `miniapp/routes/`
4. Update `miniapp/app.py` to register new blueprints

## Deployment

See the `deployment` directory for deployment scripts and instructions.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
