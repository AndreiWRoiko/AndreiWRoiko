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

# Chave secreta para sessões - obrigatória
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable is required")

# Corrige geração de URLs atrás de proxies (necessário em produção com HTTPS)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ==========================
# Configuração do Banco de Dados
# ==========================
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is required")
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
app.config["WTF_CSRF_ENABLED"] = False  # Pode ativar futuramente

# ==========================
# Inicialização do Banco
# ==========================
db = SQLAlchemy(app, model_class=Base)

# ==========================
# Importação das Rotas
# ==========================
from routes import *  # noqa: E402, F403

# ==========================
# Criação das Tabelas
# ==========================
with app.app_context():
    import models  # noqa: F401
    db.create_all()
    logging.info("✅ Tabelas do banco de dados criadas com sucesso")

# ==========================
# Execução da Aplicação
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
