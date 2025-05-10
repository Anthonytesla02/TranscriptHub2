# TranscriptHub - YouTube Transcript Extractor

TranscriptHub is a Flask web application that allows users to extract transcripts from YouTube videos, save them for future reference, and generate AI-powered summaries.

## Features

- Extract transcripts from any YouTube video with subtitles
- User authentication with secure login/signup
- Save transcripts to your personal dashboard
- Generate AI-powered summaries of transcripts
- Chat with an AI assistant about the transcript content

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Bootstrap 5, Font Awesome
- **APIs**: YouTube Transcript API, Mistral AI for summaries and chat

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Mistral API key (optional, a demo key is included)

### Running the Application

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables (optional):
   - `DATABASE_URL`: PostgreSQL connection string (provided by Replit)
   - `MISTRAL_API_KEY`: Your Mistral AI API key for summaries and chat

3. Run the application:
   ```
   ./start.sh
   ```

4. Access the application at: http://localhost:5000

### Test Account

A test account is automatically created for demonstration:
- Username: `testuser`
- Password: `password123`

## Usage

1. Sign up or log in to your account
2. Paste a YouTube URL into the extraction form
3. View the extracted transcript with timestamps
4. Generate an AI summary of the content
5. Start a chat session to ask questions about the transcript

## License

This project is open-source and available under the MIT License.