"""
Vercel serverless function entrypoint for TranscriptHub application.
"""
import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

try:
    # Import the Flask app - this will also initialize the database and register all routes
    from api.app import app
    
    # Make sure debug is off for production
    app.debug = False
    
    # Print app configuration for verification
    logger.info(f"App initialized with SQLAlchemy URI configured")
    logger.info(f"Templates will be loaded from: {app.template_folder}")
    logger.info(f"Static files will be served from: {app.static_folder}")
except Exception as e:
    logger.error(f"Error initializing app: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# WSGI handler
def handler(request):
    """
    Main handler for Vercel serverless function requests
    """
    return app(request["body"], request["headers"])

# Export the Flask application
app.debug = False
application = app
index = app