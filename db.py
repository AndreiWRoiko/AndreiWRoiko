"""
Configuração de Banco de Dados - Equipment Inventory System
Arquivo separado para facilitar implantação em diferentes ambientes
"""
import os
from typing import Dict, Any

class DatabaseConfig:
    """Configuração base do banco de dados"""
    
    @staticmethod
    def get_replit_config() -> Dict[str, Any]:
        """Configuração para ambiente Replit (usando variáveis de ambiente do Replit)"""
        return {
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20,
                'max_overflow': 10,
                'pool_size': 5,
            }
        }
    
    @staticmethod
    def get_local_config() -> Dict[str, Any]:
        """Configuração para servidor local (PostgreSQL local)"""
        # Estas configurações podem ser modificadas para seu ambiente local
        return {
            'DATABASE_URL': 'postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db',
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20,
                'max_overflow': 10,
                'pool_size': 10,  # Mais conexões para servidor local
            }
        }
    
    @staticmethod
    def get_local_mysql_config() -> Dict[str, Any]:
        """Configuração alternativa para MySQL local"""
        return {
            'DATABASE_URL': 'mysql+pymysql://inventory_user:inventory_pass@localhost:3306/inventory_db',
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_timeout': 20,
                'max_overflow': 20,
                'pool_size': 10,
            }
        }
    
    @staticmethod
    def get_sqlite_config() -> Dict[str, Any]:
        """Configuração para SQLite (desenvolvimento)"""
        return {
            'DATABASE_URL': 'sqlite:///inventory.db',
            'SQLALCHEMY_ENGINE_OPTIONS': {}
        }
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """Configuração para produção (servidor dedicado)"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise EnvironmentError(
                "DATABASE_URL é obrigatória para ambiente de produção. "
                "Configure a variável de ambiente DATABASE_URL com a URL de conexão do banco de dados."
            )
        
        return {
            'DATABASE_URL': database_url,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 30,
                'max_overflow': 20,
                'pool_size': 15,
                'echo': False,  # Desabilitar logs SQL em produção
            }
        }

def get_database_config(environment: str = None) -> Dict[str, Any]:
    """
    Retorna a configuração do banco de dados baseada no ambiente
    
    Args:
        environment: 'replit', 'local', 'local_mysql', 'sqlite', 'production'
    
    Returns:
        Dict com configuração do banco de dados
    """
    
    # Auto-detectar ambiente se não especificado
    if environment is None:
        if os.environ.get('REPL_ID'):  # Detecta se está rodando no Replit
            environment = 'replit'
        elif os.environ.get('FLASK_ENV') == 'production':
            environment = 'production'
        else:
            environment = 'local'
    
    config_map = {
        'replit': DatabaseConfig.get_replit_config(),
        'local': DatabaseConfig.get_local_config(),
        'local_mysql': DatabaseConfig.get_local_mysql_config(),
        'sqlite': DatabaseConfig.get_sqlite_config(),
        'production': DatabaseConfig.get_production_config(),
    }
    
    config = config_map.get(environment, DatabaseConfig.get_local_config())
    
    # Validar se DATABASE_URL está configurada
    if not config.get('DATABASE_URL'):
        raise ValueError(f"DATABASE_URL não configurada para ambiente: {environment}")
    
    return config

def get_connection_string(environment: str = None) -> str:
    """Retorna apenas a string de conexão do banco"""
    config = get_database_config(environment)
    return config['DATABASE_URL']

def get_engine_options(environment: str = None) -> Dict[str, Any]:
    """Retorna apenas as opções do engine SQLAlchemy"""
    config = get_database_config(environment)
    return config.get('SQLALCHEMY_ENGINE_OPTIONS', {})

# Configurações específicas para diferentes ambientes
ENVIRONMENTS = {
    'replit': 'Ambiente Replit com PostgreSQL gerenciado',
    'local': 'Servidor local com PostgreSQL',
    'local_mysql': 'Servidor local com MySQL',
    'sqlite': 'Desenvolvimento com SQLite',
    'production': 'Servidor de produção',
}

def print_environment_info():
    """Exibe informações sobre os ambientes disponíveis"""
    print("🗄️  Ambientes de banco de dados disponíveis:")
    for env, description in ENVIRONMENTS.items():
        print(f"  • {env}: {description}")
    print("\n💡 Para usar um ambiente específico, defina a variável DB_ENVIRONMENT")
    print("   Exemplo: export DB_ENVIRONMENT=local")

def mask_database_url(url: str) -> str:
    """Mascara credenciais na URL do banco de dados para logs seguros"""
    if not url:
        return "None"
    
    # Mascarar senha na URL do banco
    import re
    # Padrão para URLs com senha: protocol://user:password@host:port/database
    pattern = r'(://[^:]+:)[^@]+(@)'
    masked_url = re.sub(pattern, r'\1***\2', url)
    return masked_url

if __name__ == '__main__':
    print_environment_info()
    
    # Testar configuração atual
    try:
        current_env = os.environ.get('DB_ENVIRONMENT', 'auto-detect')
        config = get_database_config()
        print(f"\n✅ Configuração atual ({current_env}):")
        print(f"   DATABASE_URL: {mask_database_url(config['DATABASE_URL'])}")
        print(f"   Engine options: {list(config['SQLALCHEMY_ENGINE_OPTIONS'].keys())}")
    except Exception as e:
        print(f"\n❌ Erro na configuração: {e}")