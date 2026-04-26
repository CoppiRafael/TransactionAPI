import sqlite3

from database.connection import CursorSqlite


class Plan(CursorSqlite):
    """
    Acesso à tabela 'plan'.

    Schema real:  id | name | description | credit_limit
    (sem price, sem created_at — CORRIGIDO da versão anterior)

    p = Plan(conn)
    p.create(name='Basic', description='Plano básico', credit_limit=1000.0)
    row = p.get_by_id(1)  →  row["name"], row["credit_limit"], ...
    """

    def create(self, name: str, description: str = "", credit_limit: float = 0.0) -> bool:
        """Insere um novo plano."""
        # CORRIGIDO: versão anterior usava colunas 'price' e 'created_at' que não existem no schema
        if not self._validate(name, credit_limit):
            return False
        try:
            self.cursor.execute(
                "INSERT INTO plan (name, description, credit_limit) VALUES (?, ?, ?)",
                (name, description, credit_limit),
            )
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao criar plano: {e}")
            self.rollback()
            return False

    def get_by_id(self, plan_id: int) -> sqlite3.Row | None:
        """Retorna o plano com o id informado, ou None se não existir."""
        try:
            self.cursor.execute("SELECT * FROM plan WHERE id = ?", (plan_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao buscar plano: {e}")
            return None

    def get_all(self, lines: int = -1) -> list[sqlite3.Row]:
        """Retorna todos os planos."""
        try:
            if lines > 0:
                self.cursor.execute("SELECT * FROM plan LIMIT ?", (lines,))
            else:
                self.cursor.execute("SELECT * FROM plan")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar planos: {e}")
            return []

    @staticmethod  # correto: só valida strings/números, não toca no banco
    def _validate(name: str, credit_limit: float) -> bool:
        """Validação local de formato."""
        if not name.strip():
            print("Nome do plano não pode ser vazio.")
            return False
        if credit_limit < 0:
            print("Limite de crédito não pode ser negativo.")
            return False
        return True