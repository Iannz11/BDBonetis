import sqlite3

conn = sqlite3.connect("gestao_clientes.db") #Cria o banco de dados se não existir.
conn.execute("PRAGMA foreign_keys = ON") #Habilita o suporte a chaves estrangeiras.

cursor = conn.cursor() #Cria um cursor para executar comandos SQL.


#Executando vários comandos sql de uma só vez. Criando as tabelas "clientes" e "cliente_telefones".
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

conn.commit() #Salva as alterações no banco de dados.
conn.close() #Fecha a conexão com o banco de dados.

print("Banco de dados e tabelas criados.")
