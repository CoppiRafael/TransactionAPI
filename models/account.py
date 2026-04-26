import datetime
import sqlite3

from database.connection import CursorSqlite


class Account(CursorSqlite):
    """
    Acesso à tabela 'account'.

    acc = Account(conn)
    acc.create(customer_id=1, type='checking')
    row = acc.get_by_id(1)  →  row["balance"], row["type"], ...
    """

    def create(self, customer_id: int, type: str, balance: float = 0.0) -> bool:
        """Insere uma nova conta. Retorna True se criou com sucesso."""
        if not self._validate(customer_id, type, balance):
            return False
        try:
            self.cursor.execute(
                "INSERT INTO account (customer_id, type, balance, created_at) VALUES (?, ?, ?, ?)",
                (customer_id, type, balance, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            )
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao criar conta: {e}")
            self.rollback()
            return False

    def get_by_id(self, account_id: int) -> sqlite3.Row | None:
        """Retorna a conta com o id informado, ou None se não existir."""
        try:
            self.cursor.execute("SELECT * FROM account WHERE id = ?", (account_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao buscar conta: {e}")
            return None

    def get_by_customer(self, customer_id: int) -> list[sqlite3.Row]:
        """Retorna todas as contas de um cliente."""
        try:
            self.cursor.execute("SELECT * FROM account WHERE customer_id = ?", (customer_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar contas do cliente: {e}")
            return []

    def get_all(self, lines: int = -1) -> list[sqlite3.Row]:
        """Retorna todas as contas. Se lines > 0, limita a quantidade retornada."""
        try:
            if lines > 0:
                self.cursor.execute("SELECT * FROM account LIMIT ?", (lines,))
            else:
                self.cursor.execute("SELECT * FROM account")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar contas: {e}")
            return []

    def update_balance(self, account_id: int, new_balance: float) -> bool:
        """Atualiza o saldo da conta."""
        if new_balance < 0:
            print("Saldo não pode ser negativo.")
            return False
        try:
            self.cursor.execute("UPDATE account SET balance = ? WHERE id = ?", (new_balance, account_id))
            self.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar saldo: {e}")
            self.rollback()
            return False

    def delete(self, account_id: int) -> bool:
        """Deleta a conta."""
        try:
            self.cursor.execute("DELETE FROM account WHERE id = ?", (account_id,))
            self.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao deletar conta: {e}")
            self.rollback()
            return False

    def cpf_already_has_account(self, cpf: str) -> bool:
        """Verifica se o CPF já está vinculado a alguma conta."""
        try:
            self.cursor.execute(
                "SELECT a.id FROM account a JOIN customer c ON c.id = a.customer_id WHERE c.cpf = ?",
                (cpf,),
            )
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Erro ao verificar CPF: {e}")
            return False

    def _validate(self, customer_id: int, type: str, balance: float) -> bool:
        """Valida dados antes de criar a conta: cliente existe, tipo válido, saldo >= 0."""
        try:
            self.cursor.execute("SELECT id FROM customer WHERE id = ?", (customer_id,))
            if self.cursor.fetchone() is None:
                raise ValueError(f"Cliente {customer_id} não encontrado.")
            if type not in ('checking', 'savings'):
                raise ValueError(f"Tipo inválido: '{type}'. Use 'checking' ou 'savings'.")
            if balance < 0:
                raise ValueError("Saldo inicial não pode ser negativo.")
            return True
        except ValueError as e:
            print(f"Validação falhou: {e}")
            return False
        except sqlite3.Error as e:
            print(f"Erro no banco durante validação: {e}")
            return False