import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# ==========================
# Configuração de Logging
# ==========================
logging.basicConfig(level=logging.DEBUG)

# ==========================
# Classe Base do SQLAlchemy
# ==========================
class Base(DeclarativeBase):
    pass

# ==========================
# Inicialização do Flask
# ==========================
app = Flask(__name__)

# Chave secreta para sessões - com fallback para desenvolvimento
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    # Fallback para desenvolvimento - gera uma chave temporária
    import secrets
    app.secret_key = secrets.token_hex(32)
    logging.warning("⚠️  Usando chave secreta temporária para desenvolvimento. Configure SESSION_SECRET para produção!")

# Corrige geração de URLs atrás de proxies (necessário em produção com HTTPS)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ==========================
# Configuração do Banco de Dados
# ==========================
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fallback para SQLite em desenvolvimento
    database_url = "sqlite:///instance/app.db"
    logging.warning("⚠️  Usando SQLite para desenvolvimento. Configure DATABASE_URL para PostgreSQL em produção!")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # SQLite não precisa de configurações de pool
else:
    # Configurações otimizadas para PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

# ==========================
# Configuração de Uploads
# ==========================
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limite de 16MB por arquivo
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")

# ==========================
# Configuração de CSRF
# ==========================
app.config["WTF_CSRF_ENABLED"] = True  # Ativado para segurança

# ==========================
# Inicialização do Banco
# ==========================
db = SQLAlchemy(app, model_class=Base)

# ==========================
# Importação das Rotas
# ==========================
from routes import *  # noqa: E402, F403

# ==========================
# Context Processor para Permissões
# ==========================
from auth_decorators import inject_user_permissions
app.context_processor(inject_user_permissions)

# ==========================
# Criação das Tabelas
# ==========================
with app.app_context():
    import models  # noqa: F401
    db.create_all()
    logging.info("✅ Tabelas do banco de dados criadas com sucesso")
    
    # Verificar se existe pelo menos um administrador no sistema
    from models import User
    admin_count = User.query.filter_by(role='ADM', status='Aprovado').count()
    if admin_count == 0:
        logging.warning("⚠️  AVISO: Nenhum administrador encontrado no sistema!")
        logging.warning("⚠️  Para criar o primeiro administrador, execute:")
        logging.warning("⚠️  python -c \"from app import app, db; from models import User; with app.app_context(): admin = User.create_admin_user('seu_admin', 'admin@empresa.com', 'senha_segura'); db.session.add(admin); db.session.commit(); print('Admin criado!')\"")
    else:
        logging.info(f"✅ Sistema tem {admin_count} administrador(es) ativo(s)")

# ==========================
# Execução da Aplicação
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
