import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main app and models
from models import db
import main

# Create and configure the app
app = main.app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)