"""
Main Flask application for TranscriptHub.
This file contains all the application initialization logic.
"""
import os
import sys
import logging
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Create the Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
           
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Fix for SSL behind proxies

# Configure application settings
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'c1a4f89c0e3e44b88ac44f3458f0d391')  # Use env var or fallback
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Get database URL from environment variables
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    logger.error("DATABASE_URL environment variable not set!")
    # Don't fail app startup, but log the error
    db_url = "postgresql://postgres:postgres@localhost:5432/postgres"  # Fallback for development
    logger.warning(f"Using fallback database URL for development")
else:
    logger.info("Database URL configured successfully")

# Set the database URI in the app config
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# Configure connection pooling for better Vercel serverless performance
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,  # Recycle connections before PostgreSQL's 300s timeout
    'pool_timeout': 20,   # Wait up to 20 seconds for a connection
    'pool_pre_ping': True,  # Verify connections before use to detect stale connections
    'pool_size': 10,      # Maximum number of connections to keep
    'max_overflow': 5     # Allow up to 5 connections beyond pool_size when needed
}

# Import or initialize extensions
from api.models import db
from api.models import User, Transcript, Chat, Message

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # type: ignore

# Close database sessions after each request
@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

# Initialize database if needed
with app.app_context():
    try:
        logger.info("Creating database tables if they don't exist...")
        db.create_all()
        logger.info("Database tables verified.")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# Import routes after app is initialized
from api.routes import *

# Run the application if executed directly
if __name__ == "__main__":
    logger.info("Starting Flask application on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)