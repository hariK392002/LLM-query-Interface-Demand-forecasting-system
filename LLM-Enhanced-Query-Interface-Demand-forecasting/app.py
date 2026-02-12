from flask import Flask
from config import config
from database.connection import close_db_connection
from routes import web_bp, api_bp
import google.generativeai as genai
from routes.forecast_routes import forecast_bp

def create_app(config_name='default'):
    '''Application factory pattern'''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register teardown
    app.teardown_appcontext(close_db_connection)
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(forecast_bp)
    
    return app

if __name__ == '__main__':
    import os
    
    print("=" * 60)
    print("🚀 Starting LLM Query Interface for M5 Database")
    print("=" * 60)
    
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    print(f"\\n📝 Configuration: {config_name}")
    print(f"   Database: {app.config['DATABASE_PATH']}")
    print(f"   Gemini Model: {app.config['GEMINI_MODEL']}")
    print(f"\\n🌐 Server running at: http://localhost:5000")
    print("=" * 60)

    print("Available Gemini models for generateContent:")
    # for m in genai.list_models():
    #     if 'generateContent' in m.supported_generation_methods:
    #         print(m.name)
    
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=5000
    )