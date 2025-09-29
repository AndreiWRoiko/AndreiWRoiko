"""
Application Factory - Flask Equipment Inventory System
"""
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from inventory_app.config import get_config
from inventory_app.extensions import db, login_manager, migrate


def create_app(config_name=None):
    """Application Factory Pattern"""
    
    # Configuração de logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Criação da aplicação Flask com caminhos corretos para templates e static
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuração
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Middleware para proxies (necessário para HTTPS)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    from inventory_app.blueprints.auth import auth_bp
    from inventory_app.blueprints.main import main_bp
    from inventory_app.blueprints.admin import admin_bp
    from inventory_app.blueprints.inventory import inventory_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    
    # Context processors
    from inventory_app.services.auth_service import inject_user_permissions
    app.context_processor(inject_user_permissions)
    
    # User loader para Flask-Login
    from inventory_app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Importar modelos (necessário para Flask-Migrate)
    with app.app_context():
        try:
            # Importar todos os modelos para registro no SQLAlchemy
            import inventory_app.models.user  # noqa: F401
            import inventory_app.models.equipment  # noqa: F401
            import inventory_app.models.kanban  # noqa: F401
            
            # Verificar se precisa criar tabelas (desenvolvimento)
            if not db.engine.dialect.has_table(db.engine.connect(), 'users'):
                logger.info("🔄 Criando tabelas do banco de dados...")
                db.create_all()
                logger.info("✅ Tabelas PostgreSQL criadas com sucesso")
            
            # Verificar administradores
            admin_count = User.query.filter_by(role='ADM', status='Aprovado').count()
            if admin_count == 0:
                logger.warning("⚠️  Nenhum administrador encontrado. Execute: flask db create-admin")
            else:
                logger.info(f"✅ Sistema tem {admin_count} administrador(es) ativo(s)")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            # Don't raise in production to allow for graceful handling
            if app.config.get('DEBUG'):
                raise
    
    logger.info("🚀 Flask Equipment Inventory System iniciado com sucesso")
    return app