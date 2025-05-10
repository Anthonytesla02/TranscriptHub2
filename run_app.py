"""
Main entry point for TranscriptHub application.
This file is specifically designed to work with Replit's execution environment.
"""
import os
import logging
import sys
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

def main():
    """Main application entry point"""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Import the app
        from main import app
        
        # Run the application
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        
        logger.info(f"Starting TranscriptHub application on {host}:{port}")
        app.run(host=host, port=port, debug=True)
    
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()