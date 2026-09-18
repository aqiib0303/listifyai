import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MODEL_PATH = os.getenv('MODEL_PATH', 'Qwen/Qwen2.5-7B-Instruct')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///listifyai.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    # Usage quota per user per day
    DAILY_GENERATION_LIMIT = int(os.getenv('DAILY_GENERATION_LIMIT', 50))