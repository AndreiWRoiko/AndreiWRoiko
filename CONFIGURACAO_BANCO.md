# Configuração de Banco de Dados

## Como usar o arquivo `db.py`

O arquivo `db.py` foi criado para facilitar a configuração do banco de dados em diferentes ambientes. Aqui estão as instruções para usar no seu servidor local:

## Ambientes Disponíveis

### 1. **Replit** (padrão no Replit)
```bash
# Detectado automaticamente no Replit
# Usa as variáveis de ambiente do Replit
```

### 2. **Servidor Local PostgreSQL**
```bash
export DB_ENVIRONMENT=local
# Edite o arquivo db.py para configurar suas credenciais:
# 'postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db'
```

### 3. **Servidor Local MySQL**
```bash
export DB_ENVIRONMENT=local_mysql
# Configuração para MySQL:
# 'mysql+pymysql://inventory_user:inventory_pass@localhost:3306/inventory_db'
```

### 4. **SQLite (desenvolvimento)**
```bash
export DB_ENVIRONMENT=sqlite
# Usa arquivo local: 'sqlite:///inventory.db'
```

### 5. **Produção**
```bash
export DB_ENVIRONMENT=production
export DATABASE_URL="sua_url_de_producao_aqui"
```

## Passos para Servidor Local

### 1. Configurar PostgreSQL Local
```sql
-- Criar usuário e banco
CREATE USER inventory_user WITH PASSWORD 'inventory_pass';
CREATE DATABASE inventory_db OWNER inventory_user;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
```

### 2. Editar Configurações no `db.py`
```python
def get_local_config() -> Dict[str, Any]:
    """Configuração para servidor local (PostgreSQL local)"""
    return {
        'DATABASE_URL': 'postgresql://SEU_USUARIO:SUA_SENHA@localhost:5432/SEU_BANCO',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 10,
            'pool_size': 10,
        }
    }
```

### 3. Configurar Ambiente e Executar
```bash
# Definir ambiente
export DB_ENVIRONMENT=local

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python main.py
```

## Testando a Configuração

Execute este comando para testar a configuração:
```bash
python db.py
```

Isso mostrará as configurações disponíveis e testará a configuração atual.

## Variáveis de Ambiente Importantes

- `DB_ENVIRONMENT`: Define qual configuração usar
- `DATABASE_URL`: URL de conexão (usado em produção)
- `SESSION_SECRET`: Chave secreta da aplicação

## Exemplo de Deploy Local

```bash
# 1. Clonar o projeto
git clone <seu-repositorio>
cd <pasta-do-projeto>

# 2. Configurar ambiente
export DB_ENVIRONMENT=local
export SESSION_SECRET="sua-chave-secreta-aqui"

# 3. Instalar dependências
uv sync

# 4. Configurar banco PostgreSQL local
# (seguir passos do PostgreSQL acima)

# 5. Executar aplicação
python main.py
```

A aplicação estará disponível em: http://localhost:5000

## Usuário Administrador

- **Usuário:** admin
- **Senha:** Admin123!

## Suporte

Se houver problemas com a configuração, verifique:
1. Se o PostgreSQL está rodando
2. Se as credenciais estão corretas no `db.py`
3. Se a variável `DB_ENVIRONMENT` está definida corretamente