"""
Script to run the app locally for development.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app
from api.app import app

if __name__ == "__main__":
    # Get port from environment or use default (5000)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    print(f"Starting TranscriptHub on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)