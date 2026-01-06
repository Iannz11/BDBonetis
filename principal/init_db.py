import sqlite3

conn = sqlite3.connect("gestao_clientes.db")
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    cpf TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    endereco TEXT,
    localidade TEXT,
    data_nascimento TEXT,
    status INTEGER
);

CREATE TABLE IF NOT EXISTS cliente_telefones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT,
    tipo TEXT,
    cliente_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);
""")

conn.commit()
conn.close()

print("Deu certo Criar o Banco de dados!")
