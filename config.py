import os
from datetime import timedelta

class Config:
    # Clé secrète pour la sécurité des sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fraud-detection-secret-key-2024-change-in-production'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fraud_detection.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@frauddetect.com')
    
    # Configuration SMS (Twilio) - Optionnel
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
    
    # Configuration API Bancaire - Simulation
    BANK_API_URL = os.environ.get('BANK_API_URL', 'https://api.sandbox.bank.com')
    BANK_API_KEY = os.environ.get('BANK_API_KEY', 'demo-key-12345')
    
    # Configuration Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Configuration Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Langues supportées
    LANGUAGES = ['fr', 'en']
    BABEL_DEFAULT_LOCALE = 'fr'
    
    # Configuration Admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@frauddetect.com')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Configuration Sécurité
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Configuration Modèle ML
    MODEL_PATH = os.environ.get('MODEL_PATH', 'model/')
    TRAINING_DATA_PATH = os.environ.get('TRAINING_DATA_PATH', 'data/')
    
    # Debug et Testing
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False
    
    # Base de données de développement
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fraud_detection_dev.db'
    
    # Email en mode développement (console)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = False
    
    # Base de données de test
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Désactiver CSRF pour les tests
    WTF_CSRF_ENABLED = False
    
    # Email en mode test
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False
    
    # Sécurité renforcée en production
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Doit être défini en production
    
    # Base de données production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Configuration email production
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


# Mapping des configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retourne la configuration basée sur la variable d'environnement"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])