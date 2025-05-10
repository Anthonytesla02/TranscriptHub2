import os
import sys
import logging
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

try:
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded")

    # Verify database connection
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set!")
    else:
        logger.info(f"Database URL found: {db_url[:10]}...")

    # Import the main app and models
    from models import db
    import main

    # Create and configure the app
    app = main.app
    logger.info("Flask app initialized successfully")

    if __name__ == "__main__":
        logger.info("Starting Flask application on port 5000")
        app.run(host="0.0.0.0", port=5000, debug=True)
except Exception as e:
    logger.error(f"Error in app.py: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())