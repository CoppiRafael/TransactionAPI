import sqlite3

from database.connection import CursorSqlite


class Transaction(CursorSqlite):
    """
    Acesso à tabela 'bank_transaction'.
    Toda operação financeira (saque, depósito, transferência) atualiza o saldo
    e registra a transação — tudo no mesmo commit, garantindo consistência.
    """

    def deposit(self, account_id: int, amount: float) -> bool:
        """Deposita um valor na conta."""
        if not self._validate(account_id, amount):
            return False
        try:
            balance = self._get_balance(account_id)
            if balance is None:
                return False
            self._update_balance(account_id, balance + amount)
            self._record(account_id, 'deposit', amount)
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao realizar depósito: {e}")
            self.rollback()
            return False

    def withdraw(self, account_id: int, amount: float) -> bool:
        """Realiza um saque. Falha se saldo insuficiente."""
        if not self._validate(account_id, amount):
            return False
        try:
            balance = self._get_balance(account_id)
            if balance is None:
                return False
            if balance < amount:
                print("Saldo insuficiente para saque.")
                return False
            self._update_balance(account_id, balance - amount)
            self._record(account_id, 'withdraw', amount)
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao realizar saque: {e}")
            self.rollback()
            return False

    def transfer(self, from_account_id: int, to_account_id: int, amount: float) -> bool:
        """Transfere entre contas. Atômico: ou os dois saldos mudam, ou nenhum."""
        if not self._validate(from_account_id, amount):
            return False
        if not self._validate(to_account_id, amount):
            return False
        try:
            balance_from = self._get_balance(from_account_id)
            balance_to   = self._get_balance(to_account_id)
            if balance_from is None or balance_to is None:
                return False
            if balance_from < amount:
                print("Saldo insuficiente para transferência.")
                return False
            self._update_balance(from_account_id, balance_from - amount)
            self._update_balance(to_account_id,   balance_to   + amount)
            self._record(from_account_id, 'transfer_out', amount)
            self._record(to_account_id,   'transfer_in',  amount)
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao realizar transferência: {e}")
            self.rollback()
            return False

    def get_by_account(self, account_id: int) -> list[sqlite3.Row]:
        """Retorna todas as transações de uma conta."""
        try:
            self.cursor.execute(
                "SELECT * FROM bank_transaction WHERE account_id = ? ORDER BY created_at DESC",
                (account_id,),
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar transações: {e}")
            return []

    def get_all(self, lines: int = -1) -> list[sqlite3.Row]:
        """Retorna todas as transações."""
        try:
            if lines > 0:
                self.cursor.execute("SELECT * FROM bank_transaction ORDER BY created_at DESC LIMIT ?", (lines,))
            else:
                self.cursor.execute("SELECT * FROM bank_transaction ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar transações: {e}")
            return []

    def delete(self, transaction_id: int) -> bool:
        """Deleta uma transação pelo id."""
        try:
            self.cursor.execute("DELETE FROM bank_transaction WHERE id = ?", (transaction_id,))
            self.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao deletar transação: {e}")
            self.rollback()
            return False

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_balance(self, account_id: int) -> float | None:
        """Retorna o saldo atual da conta, ou None se não encontrada."""
        self.cursor.execute("SELECT balance FROM account WHERE id = ?", (account_id,))
        row = self.cursor.fetchone()
        if row is None:
            print(f"Conta {account_id} não encontrada.")
            return None
        return row["balance"]

    def _update_balance(self, account_id: int, new_balance: float) -> None:
        """Atualiza o saldo sem fazer commit (commit fica na operação principal)."""
        self.cursor.execute("UPDATE account SET balance = ? WHERE id = ?", (new_balance, account_id))

    def _record(self, account_id: int, type: str, amount: float) -> None:
        """Registra a transação sem fazer commit."""
        self.cursor.execute(
            "INSERT INTO bank_transaction (account_id, type, amount) VALUES (?, ?, ?)",
            (account_id, type, amount),
        )

    def _validate(self, account_id: int, amount: float) -> bool:
        """Valida amount > 0 e que a conta existe."""
        if amount <= 0:
            print("Valor deve ser positivo.")
            return False
        try:
            self.cursor.execute("SELECT id FROM account WHERE id = ?", (account_id,))
            if self.cursor.fetchone() is None:
                print(f"Conta {account_id} não encontrada.")
                return False
            return True
        except sqlite3.Error as e:
            print(f"Erro no banco durante validação: {e}")
            return False