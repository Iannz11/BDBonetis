import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def conectar():
    return sqlite3.connect("gestao_clientes.db")

@app.route("/")
def inicio():
    return "Servidor funcionando"


#Função de adicionar clientes ao banco de dados.

@app.route("/clientes/novo", methods=["GET", "POST"])
def adicionar_cliente():
    if request.method == "POST":
        nome = request.form["nome"]
        idade = request.form["idade"]
        cpf = request.form["cpf"]
        email = request.form["email"]
        endereco = request.form["endereco"]
        localidade = request.form["localidade"]
        data_nascimento = request.form["data_nascimento"]
        status = request.form["status"]

        conexao = conectar()
        cursor = conexao.cursor()

        try:
            # Inserir cliente
            cursor.execute("""
                INSERT INTO clientes
                (nome, idade, cpf, email, endereco, localidade, data_nascimento, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, idade, cpf, email,
                endereco, localidade,
                data_nascimento, status
            ))

            cliente_id = cursor.lastrowid

            # Telefones (vem como listas)
            numeros = request.form.getlist("telefone_numero[]")
            tipos = request.form.getlist("telefone_tipo[]")

            for numero, tipo in zip(numeros, tipos):
                cursor.execute("""
                    INSERT INTO cliente_telefones (numero, tipo, cliente_id)
                    VALUES (?, ?, ?)
                """, (numero, tipo, cliente_id))

            conexao.commit()

        except Exception as erro:
            conexao.rollback()
            print("Erro:", erro)

        finally:
            conexao.close()

        return redirect(url_for("listar_clientes"))

    return render_template("adicionar_cliente.html")



#Função de listar clientes do banco de dados.
def listar_clientes(): #Inicia a função listar_clientes.

    conn = sqlite3.connect("gestao_clientes.db") #Conecta ao banco de dados SQLite chamado "gestao_clientes.db".
    cursor = conn.cursor() #Cria um cursor para executar comandos SQL.

    cursor.execute("""
        SELECT id, nome, cpf, email
        FROM clientes
    """)

    clientes = cursor.fetchall() #Busca todos os resultados da consulta SQL e os armazena na variável clientes.
    conn.close() #Fecha a conexão com o banco de dados.

    return clientes #Por fim, temos a lista de clientes retornada pela função.

@app.route("/clientes")
def clientes():
    dados = listar_clientes()
    return render_template("clientes.html", clientes=dados)


@app.route("/teste-inserir")
def teste_inserir():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes (nome, idade, cpf, email, status)
        VALUES ('Teste', 18, '12345678901', 'teste@email.com', 1)
    """)

    conn.commit()
    conn.close()

    return "Cliente inserido"


if __name__ == "__main__":
    app.run(debug=True) 




#Função de deletar clientes do banco de dados.
@app.route("/clientes/deletar/<int:id_cliente>")
def deletar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    try:
        # Deletar telefones primeiro (relacionamento)
        cursor.execute(
            "DELETE FROM cliente_telefones WHERE cliente_id = ?",
            (id_cliente,)
        )

        # Deletar cliente
        cursor.execute(
            "DELETE FROM clientes WHERE id = ?",
            (id_cliente,)
        )

        conn.commit()

    except Exception as erro:
        conn.rollback()
        return f"Erro ao deletar cliente: {erro}"

    finally:
        conn.close()

    # Volta para a listagem
    return redirect(url_for("clientes"))
