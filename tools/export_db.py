#!/usr/bin/env python3
"""
Script para exportar todo o banco de dados para um arquivo SQLite (.db)
que pode ser usado em outros sistemas.

Uso:
    python tools/export_db.py --output database_export.db

Este script exporta:
- Todas as tabelas e suas estruturas
- Todos os dados
- Relacionamentos e chaves estrangeiras
- Índices quando possível
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError


def get_table_row_count(table_name):
    """Obtém o número de linhas de uma tabela"""
    try:
        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()
    except Exception as e:
        print(f"Erro ao contar linhas da tabela {table_name}: {e}")
        return 0


def export_database_to_sqlite(output_file):
    """
    Exporta todo o banco de dados atual para um arquivo SQLite
    """
    print(f"🔄 Iniciando exportação do banco de dados para {output_file}")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Remove arquivo anterior se existir
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"🗑️  Arquivo anterior removido: {output_file}")
    
    # Cria conexão SQLite
    sqlite_conn = sqlite3.connect(output_file)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Desabilita verificação de chaves estrangeiras temporariamente
    sqlite_cursor.execute("PRAGMA foreign_keys = OFF")
    
    try:
        with app.app_context():
            # Obtém informações sobre todas as tabelas
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            
            print(f"📊 Encontradas {len(table_names)} tabelas para exportar:")
            for table_name in table_names:
                row_count = get_table_row_count(table_name)
                print(f"   - {table_name}: {row_count} registros")
            
            total_rows_exported = 0
            
            # Exportar cada tabela
            for table_name in table_names:
                print(f"\n🔄 Exportando tabela: {table_name}")
                
                try:
                    # Obter estrutura da tabela
                    columns = inspector.get_columns(table_name)
                    primary_keys = inspector.get_pk_constraint(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    indexes = inspector.get_indexes(table_name)
                    
                    # Criar comando CREATE TABLE
                    create_sql = f"CREATE TABLE {table_name} ("
                    
                    # Obter informações sobre índices únicos antes de criar colunas
                    unique_constraints = inspector.get_unique_constraints(table_name)
                    
                    # Adicionar colunas
                    column_definitions = []
                    unique_columns = set()
                    pk_columns = set(primary_keys['constrained_columns']) if primary_keys['constrained_columns'] else set()
                    
                    # Identificar colunas com restrições únicas
                    for constraint in unique_constraints:
                        unique_columns.update(constraint['column_names'])
                    
                    for column in columns:
                        # Converter tipos SQLAlchemy para SQLite
                        col_type = str(column['type'])
                        if 'VARCHAR' in col_type.upper():
                            col_type = 'TEXT'
                        elif 'INTEGER' in col_type.upper():
                            col_type = 'INTEGER'
                        elif 'BOOLEAN' in col_type.upper():
                            col_type = 'INTEGER'
                        elif 'DATETIME' in col_type.upper():
                            col_type = 'TEXT'
                        elif 'TEXT' in col_type.upper():
                            col_type = 'TEXT'
                        else:
                            col_type = 'TEXT'  # Default fallback
                        
                        col_def = f'"{column["name"]}" {col_type}'
                        
                        # Para chaves primárias INTEGER únicas, usar PRIMARY KEY na definição da coluna
                        # para preservar auto-increment no SQLite
                        if (column['name'] in pk_columns and 
                            col_type == 'INTEGER' and 
                            len(pk_columns) == 1):
                            col_def += " PRIMARY KEY"
                        elif not column['nullable']:
                            col_def += " NOT NULL"
                        
                        # Adicionar UNIQUE para colunas que precisam ser únicas (exceto PK)
                        if column['name'] in unique_columns and column['name'] not in pk_columns:
                            col_def += " UNIQUE"
                        
                        # Skip complex defaults that are PostgreSQL specific
                        if column['default'] is not None:
                            default_val = str(column['default'])
                            # Skip PostgreSQL-specific defaults and complex expressions
                            skip_patterns = ['nextval', 'now()', 'uuid', '::', 'regclass', 'gen_random_uuid']
                            should_skip = any(pattern in default_val.lower() for pattern in skip_patterns)
                            
                            if not should_skip and default_val and default_val.lower() not in ['true', 'false']:
                                try:
                                    # Try to convert simple defaults
                                    if col_type == 'TEXT' and not default_val.startswith("'"):
                                        col_def += f" DEFAULT '{default_val}'"
                                    elif col_type == 'INTEGER':
                                        if default_val.lower() == 'true':
                                            col_def += " DEFAULT 1"
                                        elif default_val.lower() == 'false':
                                            col_def += " DEFAULT 0"
                                        else:
                                            # Only add if it's a valid integer
                                            int(default_val)
                                            col_def += f" DEFAULT {default_val}"
                                except (ValueError, TypeError):
                                    # Skip invalid defaults
                                    pass
                            
                        column_definitions.append(col_def)
                    
                    # Adicionar restrições UNIQUE multi-coluna se existirem
                    for constraint in unique_constraints:
                        if len(constraint['column_names']) > 1:
                            unique_cols = ", ".join([f'"{col}"' for col in constraint['column_names']])
                            column_definitions.append(f"UNIQUE ({unique_cols})")
                    
                    # Adicionar chave primária (apenas para chaves compostas ou não-INTEGER)
                    if primary_keys['constrained_columns']:
                        # Só adicionar se for chave composta ou se a chave não for INTEGER single-column
                        pk_cols_list = primary_keys['constrained_columns']
                        if len(pk_cols_list) > 1:
                            # Chave primária composta
                            pk_cols = ", ".join([f'"{col}"' for col in pk_cols_list])
                            column_definitions.append(f"PRIMARY KEY ({pk_cols})")
                        else:
                            # Chave primária simples - verificar se não é INTEGER (já foi definida na coluna)
                            pk_col_name = pk_cols_list[0]
                            pk_column_info = next((col for col in columns if col['name'] == pk_col_name), None)
                            if pk_column_info:
                                col_type = str(pk_column_info['type'])
                                if 'INTEGER' not in col_type.upper():
                                    # Não é INTEGER, precisa adicionar constraint
                                    pk_cols = f'"{pk_col_name}"'
                                    column_definitions.append(f"PRIMARY KEY ({pk_cols})")
                    
                    # Adicionar chaves estrangeiras (simplificado para SQLite)
                    for fk in foreign_keys:
                        fk_cols = ", ".join([f'"{col}"' for col in fk['constrained_columns']])
                        ref_table = fk['referred_table']
                        ref_cols = ", ".join([f'"{col}"' for col in fk['referred_columns']])
                        column_definitions.append(
                            f"FOREIGN KEY ({fk_cols}) REFERENCES \"{ref_table}\" ({ref_cols})"
                        )
                    
                    create_sql += ", ".join(column_definitions) + ")"
                    
                    # Executar CREATE TABLE
                    sqlite_cursor.execute(create_sql)
                    
                    # Exportar dados
                    result = db.session.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    
                    if rows:
                        # Preparar comando INSERT
                        column_names = [col['name'] for col in columns]
                        placeholders = ", ".join(["?" for _ in column_names])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
                        
                        # Inserir dados em lotes
                        batch_size = 1000
                        for i in range(0, len(rows), batch_size):
                            batch = rows[i:i + batch_size]
                            sqlite_cursor.executemany(insert_sql, batch)
                        
                        total_rows_exported += len(rows)
                        print(f"   ✅ {len(rows)} registros exportados")
                    else:
                        print(f"   ℹ️  Tabela vazia")
                    
                    # Criar índices (se possível)
                    for index in indexes:
                        if not index['unique']:  # Índices únicos podem causar problemas
                            try:
                                index_cols = ", ".join(index['column_names'])
                                index_sql = f"CREATE INDEX idx_{table_name}_{index['name']} ON {table_name} ({index_cols})"
                                sqlite_cursor.execute(index_sql)
                            except Exception as idx_error:
                                print(f"   ⚠️  Não foi possível criar índice {index['name']}: {idx_error}")
                    
                except Exception as table_error:
                    print(f"   ❌ Erro ao exportar tabela {table_name}: {table_error}")
                    continue
            
            # Reabilitar verificação de chaves estrangeiras
            sqlite_cursor.execute("PRAGMA foreign_keys = ON")
            
            # Commit das alterações
            sqlite_conn.commit()
            
            # Verificar integridade do banco exportado
            print(f"\n🔍 Verificando integridade do banco exportado...")
            sqlite_cursor.execute("PRAGMA integrity_check")
            integrity_result = sqlite_cursor.fetchone()
            
            if integrity_result[0] == "ok":
                print("   ✅ Verificação de integridade passou")
            else:
                print(f"   ⚠️  Problemas de integridade: {integrity_result[0]}")
            
            # Estatísticas finais
            print(f"\n📊 Exportação concluída!")
            print(f"   - Total de tabelas: {len(table_names)}")
            print(f"   - Total de registros: {total_rows_exported}")
            print(f"   - Arquivo gerado: {output_file}")
            print(f"   - Tamanho do arquivo: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
            
            # Verificar contagem de registros no arquivo exportado
            print(f"\n🔢 Verificando contagens por tabela no arquivo exportado:")
            for table_name in table_names:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                exported_count = sqlite_cursor.fetchone()[0]
                original_count = get_table_row_count(table_name)
                
                if exported_count == original_count:
                    print(f"   ✅ {table_name}: {exported_count} registros (OK)")
                else:
                    print(f"   ❌ {table_name}: {exported_count} exportados, {original_count} originais")
            
    except SQLAlchemyError as e:
        print(f"❌ Erro do SQLAlchemy: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante a exportação: {e}")
        return False
    finally:
        sqlite_conn.close()
    
    return True


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Exportar banco de dados para arquivo SQLite"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="database_export.db",
        help="Nome do arquivo de saída (default: database_export.db)"
    )
    
    args = parser.parse_args()
    
    # Validar se as variáveis de ambiente necessárias existem
    required_env_vars = ["DATABASE_URL", "SESSION_SECRET"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("   Certifique-se de que o projeto está configurado corretamente.")
        return 1
    
    # Executar exportação
    success = export_database_to_sqlite(args.output)
    
    if success:
        print(f"\n🎉 Exportação concluída com sucesso!")
        print(f"   Arquivo: {args.output}")
        print(f"   Para usar em outro sistema:")
        print(f"   1. Copie o arquivo {args.output} para o sistema de destino")
        print(f"   2. Configure DATABASE_URL para apontar para o arquivo SQLite:")
        print(f"      DATABASE_URL=sqlite:///{args.output}")
        print(f"   3. A aplicação funcionará normalmente com os dados exportados")
        return 0
    else:
        print(f"❌ Exportação falhou. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())