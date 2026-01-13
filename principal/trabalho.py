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

# conectando ao banco de dados SQLite ALAN
def conectar_banco():
    conn = sqlite3.connect("gestao_clientes.db") 
    conn.row_factory = sqlite3.Row 
    return conn


# listando os clientes
def listar_clientes():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT id, nome, email, telefone
                   FROM clientes
                   ORDER BY id
                 """)
    clientes = cursor.fetchall()
    conn.close()

    print("\n=== LISTA DE CLIENTES ===")
    print(f"{'ID':<5} {'NOME':<20} {'CPF':<15} {'EMAIL'}")

    if not clientes:
        print("Não há clientes cadastrados.")
        return

        for cliente in clientes:
            print(
            f"{cliente['id']:<5} "
            f"{cliente['nome']:<20} "
            f"{cliente['cpf']:<15} "
            f"{cliente['email']}"
        )

    print("\nAções disponíveis por ID:")
    print("1 - Visualizar | 2 - Editar | 3 - Deletar")

def menu():
    while True:
        print("MENU DE CLIENTES: ")
        print("1 - Listar Clientes")
        print("0 - Voltar")

        escolha = input("Escolha: ")

        if escolha == "1":
            listar_clientes()
        elif escolha == "0":
            break
        else:
            print("Escoçha não existente. Tente novamente.")
        

if __name__ == "__main__":
    menu()

#Função de listar clientes do banco de dados.
@app.route("/clientes")
def listar_clientes():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, telefone
        FROM clientes
        ORDER BY id
    """)
    clientes = cursor.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)

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

#Função de editar clientes do banco de dados.

@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        novo_nome = request.form["nome"]
        nova_idade = request.form["idade"]
        novo_email = request.form["email"]
        novo_endereco = request.form["endereco"]
        nova_localidade = request.form["localidade"]
        novo_status = request.form["status"]

        try:
            cursor.execute("""
                UPDATE clientes
                SET nome = ?, idade = ?, email = ?, endereco = ?, localidade = ?, status = ?
                WHERE id = ?
            """, (
                novo_nome,
                nova_idade,
                novo_email,
                novo_endereco,
                nova_localidade,
                novo_status,
                id_cliente
            ))

            conn.commit()

        except Exception as erro:
            conn.rollback()
            return f"Erro ao atualizar cliente: {erro}"

        finally:
            conn.close()

        return redirect(url_for("clientes"))

    # GET → buscar dados atuais
    cursor.execute("""
        SELECT nome, idade, email, endereco, localidade, status
        FROM clientes
        WHERE id = ?
    """, (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if cliente is None:
        return "Cliente não encontrado"

    return render_template("editar_cliente.html", cliente=cliente, id_cliente=id_cliente)
