import os
from datetime import timedelta


def _normalized_database_url():
    """
    Read DATABASE_URL from the environment and normalize it for SQLAlchemy.

    Render (and some other hosts) provide Postgres connection strings that
    start with "postgres://", but SQLAlchemy 1.4+/2.x requires the
    "postgresql://" scheme. Falls back to a local SQLite file when no
    DATABASE_URL is set (local development).
    """
    url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration"""
    # Database
    SQLALCHEMY_DATABASE_URI = _normalized_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY',
        'your-secret-key-change-this-in-production'
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Session (for CORS if needed)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
