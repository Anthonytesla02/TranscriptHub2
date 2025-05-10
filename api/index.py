"""
Vercel serverless function entrypoint for TranscriptHub application.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    # Import the app
    from main import app

    # For Vercel serverless functions
    app.debug = False
except Exception as e:
    logger.error(f"Error importing app: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# Create WSGI handler for Vercel
from flask import request

def handler(event, context):
    """Serverless function handler for Vercel"""
    return app(event["body"], event["headers"])

# Export the Flask application for various deployment platforms
index = app.wsgi_app
app.wsgi_app = app
application = app