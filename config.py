import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask configuration
DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Database configuration
DEFAULT_DB_PATH = os.getenv('DEFAULT_DB_PATH', 'uploads/sample.db')

# Google AI configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# OpenAI configuration (fallback)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# LLM configuration
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-pro')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0'))