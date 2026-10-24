# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import create_engine

DB_USER = "ia_reader"
DB_PASS = "test123!"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "empresa_db"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL)
    tabelas = pd.read_sql("SHOW TABLES;", engine)
    print("Conexao bem-sucedida! Tabelas encontradas:")
    print(tabelas)
    print("\n--- Dados da Tabela Vendas ---")
    print(pd.read_sql("SELECT * FROM vendas LIMIT 5;", engine))
except Exception as e:
    print(f"Erro ao conectar: {e}")
