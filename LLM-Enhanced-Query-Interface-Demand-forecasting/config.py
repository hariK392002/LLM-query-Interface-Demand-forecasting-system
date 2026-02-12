import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH')
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro-latest')
    
    # Query Limits
    MAX_QUERY_LIMIT = int(os.getenv('MAX_QUERY_LIMIT', '500'))
    DEFAULT_QUERY_LIMIT = int(os.getenv('DEFAULT_QUERY_LIMIT', '100'))
    
    # Security
    ALLOWED_SQL_OPERATIONS = ['select']
    DANGEROUS_KEYWORDS = ['drop', 'delete', 'update', 'insert', 'alter', 
                          'create', 'truncate', 'exec', 'execute', 'pragma']

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}