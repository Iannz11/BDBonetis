import sqlite3;

def conectar():
    return sqlite3.connect("gestao_clientes.db")

def deletar_cliente():
    conexao = conectar()
    cursor = conexao.cursor()

    id_cliente = input("Digite o ID do cliente que deseja deletar: ")

    # Verifica se o cliente existe
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (id_cliente,))
    cliente = cursor.fetchone()

    if cliente is None:
        print(" X Cliente não encontrado.")
        conexao.close()
        return

    print(f"Cliente encontrado: {cliente[0]}")

    confirmacao = input("Você tem certeza que deseja deletar este cliente? (s/n): ")

    if confirmacao.lower() == 's':
        try:
            # Deletar telefones
            cursor.execute(
                "DELETE FROM cliente_telefones WHERE cliente_id = ?",
                (id_cliente,)
            )

            # Deletar cliente
            cursor.execute(
                "DELETE FROM clientes WHERE id = ?",
                (id_cliente,)
            )

            conexao.commit()
            print("✅ Cliente deletado com sucesso!")

        except Exception as erro:
            conexao.rollback()
            print(" X Erro ao deletar cliente:", erro)

    else:
        print(" X Operação cancelada.")

    cursor.close()
    conexao.close()