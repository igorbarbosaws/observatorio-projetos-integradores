"""
Script de migração: adiciona coluna foto_perfil à tabela users.
Execute: python migrate.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "observatorio.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

colunas = [row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()]
print("Colunas atuais:", colunas)

if "foto_perfil" not in colunas:
    c.execute("ALTER TABLE users ADD COLUMN foto_perfil TEXT")
    conn.commit()
    print("✓ Coluna foto_perfil adicionada com sucesso.")
else:
    print("✓ Coluna foto_perfil já existe — nenhuma alteração necessária.")

conn.close()
