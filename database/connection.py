import sqlite3
from pathlib import Path

ROOT_PATH = Path(__file__).parent
DATABASE_PATH = ROOT_PATH / "bank_database.db"

# ── Schema ────────────────────────────────────────────────────────────────────

CREATE_PLAN = """
    CREATE TABLE IF NOT EXISTS plan (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE,
        description TEXT,
        credit_limit REAL   NOT NULL DEFAULT 0.0
    )
"""

CREATE_CUSTOMER = """
    CREATE TABLE IF NOT EXISTS customer (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT    NOT NULL,
        email      TEXT    NOT NULL UNIQUE,
        cpf        TEXT    NOT NULL UNIQUE,
        plan_id    INTEGER NOT NULL,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (plan_id) REFERENCES plan(id) ON DELETE RESTRICT
    )
"""

CREATE_ACCOUNT = """
    CREATE TABLE IF NOT EXISTS account (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        type        TEXT    NOT NULL CHECK(type IN ('checking', 'savings')),
        balance     REAL    NOT NULL DEFAULT 0.0,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
    )
"""

CREATE_TRANSACTION = """
    CREATE TABLE IF NOT EXISTS bank_transaction (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        type       TEXT    NOT NULL CHECK(type IN ('deposit', 'withdraw', 'transfer_in', 'transfer_out')),
        amount     REAL    NOT NULL CHECK(amount > 0),
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE
    )
"""

CREATE_HISTORY_VIEW = """
    CREATE VIEW IF NOT EXISTS history AS
        SELECT
            t.id            AS transaction_id,
            t.created_at    AS date,
            t.type,
            t.amount,
            a.id            AS account_id,
            a.type          AS account_type,
            c.id            AS customer_id,
            c.name          AS customer_name
        FROM bank_transaction t
        JOIN account  a ON a.id = t.account_id
        JOIN customer c ON c.id = a.customer_id
        ORDER BY t.created_at DESC
"""

_SCHEMA: list[str] = [
    CREATE_PLAN,
    CREATE_CUSTOMER,
    CREATE_ACCOUNT,
    CREATE_TRANSACTION,
    CREATE_HISTORY_VIEW,
]

# ── Conexão ───────────────────────────────────────────────────────────────────

def get_connection(path: Path = DATABASE_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path = DATABASE_PATH) -> None:
    with get_connection(path) as conn:
        for statement in _SCHEMA:
            conn.execute(statement)
        conn.commit()
    print(f"Banco inicializado em: {path}")


# ── Classe base ───────────────────────────────────────────────────────────────

class CursorSqlite:
    """
    Classe base que injeta conexão e cursor em todas as classes do projeto.

    Exemplo de uso em subclasse:
        class Account(CursorSqlite):
            pass   # sem __init__ próprio!

        acc = Account(conn)
        row = acc.get_by_id(5)      # retorna sqlite3.Row com os dados
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn   = conn
        self.cursor = conn.cursor()

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()