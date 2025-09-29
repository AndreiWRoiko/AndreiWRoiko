"""
Configuração da aplicação - Flask Equipment Inventory System
"""
import os
import secrets
from typing import Type


class Config:
    """Configuração base da aplicação"""
    
    # Chave secreta - obrigatória em produção
    SECRET_KEY = os.environ.get("SESSION_SECRET")
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)
    
    # Base de dados - PostgreSQL obrigatório
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise EnvironmentError("DATABASE_URL é obrigatório. Configure a conexão PostgreSQL.")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 10,
        "pool_size": 5,
    }
    
    # Configuração de uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    
    # Configuração de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configuração de sessão
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configuração para testes"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


# Mapeamento de configurações
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Type[Config]:
    """Retorna a configuração baseada no ambiente"""
    env = os.environ.get("FLASK_ENV", "default")
    return config.get(env, config["default"])