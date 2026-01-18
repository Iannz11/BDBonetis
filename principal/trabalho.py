import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# ======================
# CONEXÃO COM O BANCO
# ======================
def conectar():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "gestao_clientes.db")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# ROTA INICIAL
# ======================
@app.route("/")
def inicio():
    return redirect(url_for("listar_clientes"))


# ======================
# LISTAR CLIENTES
# ======================
@app.route("/clientes")
def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cursor.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)


# ======================
# ADICIONAR CLIENTE
# ======================
@app.route("/clientes/novo", methods=["GET", "POST"])
def adicionar_cliente():
    if request.method == "POST":
        dados = (
            request.form["nome"],
            request.form["idade"],
            request.form["cpf"],
            request.form["email"],
            request.form["endereco"],
            request.form["localidade"],
            request.form["data_nascimento"],
            request.form["status"]
        )

        conn = conectar()
        cursor = conn.cursor()

        try:
            # Insere cliente
            cursor.execute("""
                INSERT INTO clientes
                (nome, idade, cpf, email, endereco, localidade, data_nascimento, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, dados)

            cliente_id = cursor.lastrowid

            # telefones 
            numeros = request.form.getlist("telefone_numero[]")
            tipos = request.form.getlist("telefone_tipo[]")

            for numero, tipo in zip(numeros, tipos):
                cursor.execute("""
                    INSERT INTO cliente_telefones (numero, tipo, cliente_id)
                    VALUES (?, ?, ?)
                """, (numero, tipo, cliente_id))

            conn.commit()

        except Exception as erro:
            conn.rollback()
            return f"Erro ao inserir cliente: {erro}"

        finally:
            conn.close()

        return redirect(url_for("listar_clientes"))

    return render_template("adicionar.html")


# ======================
# EDITAR CLIENTE
# ======================
@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            
            cursor.execute("""
                UPDATE clientes
                SET nome = ?, idade = ?, email = ?, endereco = ?, localidade = ?, status = ?
                WHERE id = ?
            """, (
                request.form["nome"],
                request.form["idade"],
                request.form["email"],
                request.form["endereco"],
                request.form["localidade"],
                request.form["status"],
                id_cliente
            ))


#insert telefones
            ids = request.form.getlist("telefone_id[]")        # ID do telefone
            numeros = request.form.getlist("telefone_numero[]")
            tipos = request.form.getlist("telefone_tipo[]")

            for tel_id, numero, tipo in zip(ids, numeros, tipos):
                if tel_id:  # telefone existente → UPDATE
                    cursor.execute("""
                        UPDATE cliente_telefones
                        SET numero = ?, tipo = ?
                        WHERE id = ? AND cliente_id = ?
                    """, (numero, tipo, tel_id, id_cliente))
                else:       # telefone novo → INSERT
                    cursor.execute("""
                        INSERT INTO cliente_telefones (numero, tipo, cliente_id)
                        VALUES (?, ?, ?)
                    """, (numero, tipo, id_cliente))

            conn.commit()

        except Exception as erro:
            conn.rollback()
            return f"Erro ao atualizar: {erro}"

        finally:
            conn.close()

        return redirect(url_for("listar_clientes"))

    # ----------------------
    # ALTERADO: buscar cliente
    # ----------------------
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente,))
    cliente = cursor.fetchone()

    cursor.execute("""
        SELECT id, numero, tipo
        FROM cliente_telefones
        WHERE cliente_id = ?
    """, (id_cliente,))
    telefones = cursor.fetchall()

    conn.close()

    if cliente is None:
        return "Cliente não encontrado"

    return render_template("editar.html", cliente=cliente, telefones=telefones)


# ======================
# DELETAR CLIENTE
# ======================
@app.route("/clientes/deletar/<int:id_cliente>")
def deletar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM cliente_telefones WHERE cliente_id = ?",
            (id_cliente,)
        )
        cursor.execute(
            "DELETE FROM clientes WHERE id = ?",
            (id_cliente,)
        )
        conn.commit()

    except Exception as erro:
        conn.rollback()
        return f"Erro ao deletar: {erro}"

    finally:
        conn.close()

    return redirect(url_for("listar_clientes"))


# ======================
# VISUALIZAR CLIENTE
# ======================
@app.route("/clientes/visualizar/<int:id_cliente>")
def visualizar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, idade, cpf, email, endereco, localidade, status
        FROM clientes
        WHERE id = ?
    """, (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente is None:
        return "Cliente não encontrado"

    return render_template("visualizar.html", cliente=cliente)


# ======================
# EXECUÇÃO
# ======================
if __name__ == "__main__":
    app.run(debug=True)