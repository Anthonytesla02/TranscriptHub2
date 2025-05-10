"""
Database models for TranscriptHub application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy without binding to an app yet (this happens in app.py)
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication and data ownership."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    transcripts = db.relationship('Transcript', backref='user', lazy=True)
    chats = db.relationship('Chat', backref='user', lazy=True)

class Transcript(db.Model):
    """Transcript model for storing YouTube video transcripts."""
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chats = db.relationship('Chat', backref='transcript', lazy=True)

class Chat(db.Model):
    """Chat model for conversations about transcripts."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transcript_id = db.Column(db.Integer, db.ForeignKey('transcript.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    """Message model for storing conversation messages."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)