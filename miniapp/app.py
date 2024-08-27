from flask import Flask, jsonify
from routes import booking_routes, kyc_routes, car_routes
from utils.logger import get_logger

app = Flask(__name__)
logger = get_logger(__name__)

# Register blueprints
app.register_blueprint(car_routes, url_prefix='/api/car')
app.register_blueprint(booking_routes, url_prefix='/api/booking')
app.register_blueprint(kyc_routes, url_prefix='/api/kyc')

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)