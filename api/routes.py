"""
Route definitions for the TranscriptHub application.
"""
import os
import json
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from api.app import app, db
from api.models import User, Transcript, Chat, Message
from api.utils import get_chat_response, summarize_transcript

# Configure logging
logger = logging.getLogger(__name__)

# Helper function for safe database queries
def safe_db_query(query_function, default_return=None, log_prefix="Database error"):
    """
    Executes a database query function safely with error handling
    
    Args:
        query_function: A function that executes the actual database query
        default_return: The value to return if the query fails
        log_prefix: Prefix for error log messages
        
    Returns:
        The result of the query or default_return if it fails
    """
    try:
        return query_function()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"{log_prefix}: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        
        # Try to rollback the session
        try:
            db.session.rollback()
        except:
            pass
            
        return default_return

# Helper function to extract YouTube video ID from URLs
def extract_video_id(url):
    """
    Extract the YouTube video ID from various YouTube URL formats.
    
    Supports:
    - Standard YouTube URLs: https://www.youtube.com/watch?v=VIDEO_ID
    - Short YouTube URLs: https://youtu.be/VIDEO_ID
    - Embed URLs: https://www.youtube.com/embed/VIDEO_ID
    - Video URLs: https://www.youtube.com/v/VIDEO_ID
    - Mobile URLs: https://m.youtube.com/watch?v=VIDEO_ID
    - Playlist URLs: Also extracts video ID from playlist URLs
    """
    if not url:
        return None
        
    # Clean the URL
    url = url.strip()
    
    # Extract using urlparse
    parsed_url = urlparse(url)
    
    # Check for youtu.be domain (short URLs)
    if parsed_url.netloc in ['youtu.be']:
        return parsed_url.path.strip('/')
    
    # For standard or mobile YouTube domains
    if any(domain in parsed_url.netloc for domain in ['youtube.com', 'm.youtube.com', 'www.youtube.com']):
        # Handle /watch path with v parameter
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
            
        # Handle /embed/ or /v/ paths
        if '/embed/' in parsed_url.path or '/v/' in parsed_url.path:
            path_parts = parsed_url.path.split('/')
            # The ID should be after /embed/ or /v/
            for i, part in enumerate(path_parts):
                if part in ['embed', 'v'] and i < len(path_parts) - 1:
                    return path_parts[i + 1]
    
    # If all checks fail, return None
    return None

# Route definitions
@app.route('/')
def landing():
    """Landing page with pricing and features"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')

@app.route('/home')
@login_required
def index():
    """Home page for authenticated users"""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
@login_required
def extract():
    video_url = request.form.get('video_url', '').strip()
    video_id = extract_video_id(video_url)

    if not video_id:
        flash('Invalid YouTube URL provided.', 'danger')
        return redirect(url_for('index'))

    try:
        # Try with English first
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            # Fallback: try to get any available transcript if English isn't available
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Get the first available transcript
            if transcript_list:
                transcript = transcript_list[0]
                transcript_list = transcript.fetch()
            else:
                raise NoTranscriptFound(f"No transcripts found for video ID: {video_id}")
                
        # Format the transcript with timestamps
        formatted_entries = []
        for entry in transcript_list:
            # Convert timestamp to minutes:seconds format
            timestamp_seconds = int(entry['start'])
            minutes = timestamp_seconds // 60
            seconds = timestamp_seconds % 60
            timestamp = f"[{minutes:02d}:{seconds:02d}] "
            
            # Add formatted entry
            formatted_entries.append(f"{timestamp}{entry['text']}")
            
        transcript_text = "\n".join(formatted_entries)

        # Save to database
        transcript = Transcript(video_url=video_url, content=transcript_text, user_id=current_user.id)
        db.session.add(transcript)
        db.session.commit()

        # Create an automatic summary
        try:
            summary = summarize_transcript(transcript_text)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            summary = "Summary could not be generated automatically."

        return render_template('result.html', 
                              transcript=transcript_text, 
                              video_url=video_url, 
                              transcript_id=transcript.id,
                              summary=summary)

    except NoTranscriptFound:
        flash('No transcript found for this video.', 'warning')
    except TranscriptsDisabled:
        flash('Transcripts are disabled for this video.', 'warning')
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error extracting transcript: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = generate_password_hash(request.form['password'])

            # Check if username exists
            def check_username():
                return User.query.filter_by(username=username).first()
            
            existing_user = safe_db_query(
                check_username,
                default_return=None,
                log_prefix="Error checking username"
            )
            
            if existing_user:
                flash('Username already exists.', 'warning')
                return redirect(url_for('signup'))

            # Create new user
            user = User(username=username, password=password)
            
            def save_user():
                db.session.add(user)
                db.session.commit()
                return True
                
            success = safe_db_query(
                save_user,
                default_return=False,
                log_prefix="Error creating new user"
            )
            
            if success:
                # Auto-login the user after signup
                login_user(user)
                flash('Account created! Welcome to TranscriptHub.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error creating account. Please try again.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(username=request.form['username']).first()
            if user and check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid username or password.', 'danger')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Database error during login: {str(e)}")
            logger.error(f"Traceback: {error_details}")
            flash('A database connection error occurred. Please try again.', 'danger')
            
            # Try to reconnect to the database
            try:
                db.session.rollback()  # Roll back any failed transaction
            except:
                pass  # If rollback fails, we'll still want to render the login page

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        transcripts = Transcript.query.filter_by(user_id=current_user.id).order_by(Transcript.created_at.desc()).all()
        return render_template('dashboard.html', transcripts=transcripts)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Database error in dashboard: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        flash('Unable to load your transcripts. Database connection issue.', 'danger')
        
        # Try to rollback the session
        try:
            db.session.rollback()
        except:
            pass
            
        # Return empty transcripts list
        return render_template('dashboard.html', transcripts=[])

@app.route('/create_chat/<int:transcript_id>', methods=['POST'])
@login_required
def create_chat(transcript_id):
    """Create a new chat for a transcript and redirect to the chat page"""
    transcript = Transcript.query.get_or_404(transcript_id)
    
    # Verify user has access to this transcript
    if transcript.user_id != current_user.id:
        flash('You do not have permission to access this transcript.', 'danger')
        return redirect(url_for('index'))
    
    # Create a new chat
    title = f"Chat about YouTube video ({transcript.video_url})"
    chat = Chat(
        title=title,
        user_id=current_user.id,
        transcript_id=transcript_id
    )
    db.session.add(chat)
    db.session.commit()
    
    return redirect(url_for('chat', chat_id=chat.id))

@app.route('/chat/<int:chat_id>')
@login_required
def chat(chat_id):
    """Show the chat interface for a specific chat"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Verify user has access to this chat
    if chat.user_id != current_user.id:
        flash('You do not have permission to access this chat.', 'danger')
        return redirect(url_for('index'))
    
    # Get the transcript content
    transcript = Transcript.query.get(chat.transcript_id)
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    
    return render_template(
        'chat.html',
        chat=chat,
        transcript=transcript,
        messages=messages
    )

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    """API endpoint to send a message and get an AI response"""
    try:
        # Get request data
        data = request.json
        chat_id = data.get('chat_id')
        message_content = data.get('message')
        
        # Verify ownership of chat
        chat = Chat.query.get_or_404(chat_id)
        if chat.user_id != current_user.id:
            return jsonify({'error': 'You do not have permission to access this chat'}), 403
            
        # Get transcript for context
        transcript = Transcript.query.get_or_404(chat.transcript_id)
        
        # Save the user message
        user_message = Message(
            content=message_content,
            role='user',
            chat_id=chat_id
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Get all messages for context
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
        message_list = [{'role': msg.role, 'content': msg.content} for msg in messages]
        
        # Get AI response
        ai_response_content = get_chat_response(message_list, transcript.content)
        
        # Save the AI response
        ai_message = Message(
            content=ai_response_content,
            role='assistant',
            chat_id=chat_id
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'role': user_message.role,
                'timestamp': user_message.timestamp.isoformat()
            },
            'ai_message': {
                'id': ai_message.id,
                'content': ai_message.content,
                'role': ai_message.role,
                'timestamp': ai_message.timestamp.isoformat()
            }
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in send_message: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        
        return jsonify({'error': str(e)}), 500

@app.route('/chats')
@login_required
def chats():
    """Show all chats for the current user"""
    user_chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).all()
    return render_template('chats.html', chats=user_chats)