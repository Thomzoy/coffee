import sqlite3
from datetime import datetime
from typing import List, Union


class Database:
    """
    SQLite database interface for the coffee tracking application.

    Manages user data and coffee consumption records using a context manager pattern.
    """

    def __init__(self, db_name: str = "app_data.db"):
        """
        Initialize database connection parameters.

        Args:
            db_name: Path to the SQLite database file
        """
        self.db_name = db_name
        self.conn = None  # Will be initialized in __enter__

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                button_id INTEGER,
                name TEXT,
                creation_dt TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mug (
                button_id INTEGER,
                value REAL,
                mug_dt TEXT
            )
        """)

        self.conn.commit()

    def add_user(self, button_id: int, name: str, dt: datetime = None):
        """Insert a user record."""
        dt = dt or datetime.now()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO user (button_id, name, creation_dt)
            VALUES (?, ?, ?)
        """,
            (button_id, name, dt.isoformat()),
        )
        self.conn.commit()

    def add_mug(self, button_id: int, value: float, dt: datetime = None):
        """Insert a mug record."""
        dt = dt or datetime.now()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO mug (button_id, value, mug_dt)
            VALUES (?, ?, ?)
        """,
            (button_id, value, dt.isoformat()),
        )
        self.conn.commit()

    def get_mugs(self, identifier: Union[int, str], today: bool = True) -> List[dict]:
        """
        Get all mugs corresponding to a button_id or user name.
        Returns a list of dictionaries with parsed datetimes.
        """
        cursor = self.conn.cursor()

        if isinstance(identifier, int):
            query = "SELECT button_id, value, mug_dt FROM mug WHERE button_id = ?"
            params = [identifier]

        elif isinstance(identifier, str):
            query = """
                SELECT m.button_id, m.value, m.mug_dt
                FROM mug m
                JOIN user u ON m.button_id = u.button_id
                WHERE u.name = ?
            """
            params = [identifier]

        else:
            raise ValueError("Identifier must be an int (button_id) or str (name).")

        if today:
            query += " AND date(mug_dt) = date('now', 'localtime')"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for button_id, value, dt_str in rows:
            result.append(
                {
                    "button_id": button_id,
                    "value": value,
                    "datetime": datetime.fromisoformat(dt_str),
                }
            )

        return result

    def get_name(self, button_id: int) -> str:
        """
        Return the most recent name associated with a given button_id.
        Returns str(button_id) if no user is found.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT name
            FROM user
            WHERE button_id = ?
            ORDER BY datetime(creation_dt) DESC
            LIMIT 1
        """,
            (button_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else str(button_id)

    def close(self):
        """Close the database connection."""
        self.conn.close()
