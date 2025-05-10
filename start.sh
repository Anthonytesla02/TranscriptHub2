#!/bin/bash
# Start script for TranscriptHub application

# Ensure the database is set up
python -c "
import os
from flask import Flask
from models import db
import main

app = main.app
with app.app_context():
    db.create_all()
    print('Database setup complete!')
"

# Start the application using gunicorn
gunicorn -b 0.0.0.0:5000 app:app