"""
Extensões Flask - Equipment Inventory System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy"""
    pass

# Inicialização das extensões
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

# Configuração do LoginManager
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"