import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ======================
# CONEXÃO COM O BANCO
# ======================
def conectar():
    conn = sqlite3.connect("gestao_clientes.db")
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

    cursor.execute("""
        SELECT id, nome, cpf, email
        FROM clientes
        ORDER BY id
    """)
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
            cursor.execute("""
                INSERT INTO clientes
                (nome, idade, cpf, email, endereco, localidade, data_nascimento, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, dados)

            cliente_id = cursor.lastrowid

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

    return render_template("adicionar_cliente.html")


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

            conn.commit()

        except Exception as erro:
            conn.rollback()
            return f"Erro ao atualizar: {erro}"

        finally:
            conn.close()

        return redirect(url_for("listar_clientes"))

    cursor.execute("""
        SELECT *
        FROM clientes
        WHERE id = ?
    """, (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente is None:
        return "Cliente não encontrado"

    return render_template("editar_cliente.html", cliente=cliente)


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
# EXECUÇÃO
# ======================
if __name__ == "__main__":
    app.run(debug=True)






# ======================
# Rota visualizar clientes:
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

    return render_template("visualizar_cliente.html", cliente=cliente)