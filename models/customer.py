import sqlite3

from database.connection import CursorSqlite


class Customer(CursorSqlite):
    """
    Acesso à tabela 'customer'.

    c = Customer(conn)
    c.create(name='João', email='j@j.com', cpf='000.000.000-00', plan_id=1)
    row = c.get_by_id(1)  →  row["name"], row["email"], ...
    """

    def create(self, name: str, email: str, cpf: str, plan_id: int) -> bool:
        """Insere um novo cliente. Retorna True se criou com sucesso."""
        # CORRIGIDO: a versão anterior não passava cpf nem plan_id, que são NOT NULL no schema
        if not self._validate(name, email, cpf):
            return False
        try:
            self.cursor.execute(
                "INSERT INTO customer (name, email, cpf, plan_id) VALUES (?, ?, ?, ?)",
                (name, email, cpf, plan_id),
                # created_at tem DEFAULT no banco, não precisa ser enviado
            )
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao criar cliente: {e}")
            self.rollback()
            return False

    def get_by_id(self, customer_id: int) -> sqlite3.Row | None:
        """Retorna o cliente com o id informado, ou None se não existir."""
        try:
            self.cursor.execute("SELECT * FROM customer WHERE id = ?", (customer_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao buscar cliente: {e}")
            return None

    def get_all(self, lines: int = -1) -> list[sqlite3.Row]:
        """Retorna todos os clientes. Se lines > 0, limita a quantidade retornada."""
        try:
            if lines > 0:
                self.cursor.execute("SELECT * FROM customer LIMIT ?", (lines,))
            else:
                self.cursor.execute("SELECT * FROM customer")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def change_email(self, customer_id: int, new_email: str) -> bool:
        """Atualiza o email do cliente."""
        if not new_email.strip() or "@" not in new_email:
            print("Email inválido.")
            return False
        try:
            self.cursor.execute("UPDATE customer SET email = ? WHERE id = ?", (new_email, customer_id))
            self.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar email: {e}")
            self.rollback()
            return False

    def delete(self, customer_id: int) -> bool:
        """Deleta o cliente. Por CASCADE, também apaga as contas vinculadas."""
        try:
            self.cursor.execute("DELETE FROM customer WHERE id = ?", (customer_id,))
            self.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao deletar cliente: {e}")
            self.rollback()
            return False

    @staticmethod  # correto aqui: não usa self.cursor, só valida strings
    def _validate(name: str, email: str, cpf: str) -> bool:
        """Validação local de formato — não toca no banco."""
        if not name.strip():
            print("Nome não pode ser vazio.")
            return False
        if not email.strip() or "@" not in email:
            print("Email inválido.")
            return False
        if not cpf.strip():
            print("CPF não pode ser vazio.")
            return False
        return True