"""SQLite helper.

Ported from ServiceLib/Helper/SqliteHelper.cs.
Uses sqlite3 standard library with aiosqlite for async operations.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any, TypeVar

from v2rayn.common import logging_config

_tag = "SqliteHelper"
T = TypeVar("T")


class SqliteHelper:
    """SQLite database helper for v2rayN configuration storage."""

    def __init__(self, db_path: str):
        """Initialize SQLite helper.

        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self._db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
        return self._connection

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, sql: str, params: tuple = ()) -> None:
        """Execute a SQL statement.

        Args:
            sql: SQL statement
            params: Statement parameters
        """
        try:
            conn = self.get_connection()
            conn.execute(sql, params)
            conn.commit()
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    def execute_many(self, sql: str, params_list: list[tuple]) -> None:
        """Execute a SQL statement for multiple parameter sets.

        Args:
            sql: SQL statement
            params_list: List of parameter tuples
        """
        try:
            conn = self.get_connection()
            conn.executemany(sql, params_list)
            conn.commit()
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute a query and return results as list of dicts.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return []

    def query_single(self, sql: str, params: tuple = ()) -> dict | None:
        """Execute a query and return a single result.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            Result dictionary or None
        """
        results = self.query(sql, params)
        return results[0] if results else None

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists.

        Args:
            table_name: Table name to check

        Returns:
            True if table exists
        """
        result = self.query_single(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return result is not None

    def create_table(self, table_name: str, columns: dict[str, str], primary_key: str | None = None) -> None:
        """Create a table if it doesn't exist.

        Args:
            table_name: Table name
            columns: Dictionary of column_name -> column_type
            primary_key: Optional primary key column name
        """
        col_defs = []
        for name, col_type in columns.items():
            definition = f"{name} {col_type}"
            if name == primary_key:
                definition += " PRIMARY KEY"
            col_defs.append(definition)

        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
        self.execute(sql)

    def insert(self, table_name: str, data: dict[str, Any]) -> None:
        """Insert a row into a table.

        Args:
            table_name: Table name
            data: Dictionary of column_name -> value
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute(sql, tuple(data.values()))

    def update(self, table_name: str, data: dict[str, Any], where: str, where_params: tuple = ()) -> None:
        """Update rows in a table.

        Args:
            table_name: Table name
            data: Dictionary of column_name -> value
            where: WHERE clause
            where_params: WHERE clause parameters
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
        self.execute(sql, tuple(data.values()) + where_params)

    def delete(self, table_name: str, where: str, where_params: tuple = ()) -> None:
        """Delete rows from a table.

        Args:
            table_name: Table name
            where: WHERE clause
            where_params: WHERE clause parameters
        """
        sql = f"DELETE FROM {table_name} WHERE {where}"
        self.execute(sql, where_params)

    def count(self, table_name: str, where: str = "", where_params: tuple = ()) -> int:
        """Count rows in a table.

        Args:
            table_name: Table name
            where: Optional WHERE clause
            where_params: WHERE clause parameters

        Returns:
            Row count
        """
        sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        result = self.query_single(sql, where_params)
        return result["cnt"] if result else 0

    async def execute_async(self, sql: str, params: tuple = ()) -> None:
        """Execute a SQL statement asynchronously.

        Args:
            sql: SQL statement
            params: Statement parameters
        """
        try:
            import aiosqlite

            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(sql, params)
                await db.commit()
        except ImportError:
            # Fallback to sync
            self.execute(sql, params)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)

    async def query_async(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute a query asynchronously.

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            import aiosqlite

            async with aiosqlite.connect(self._db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except ImportError:
            # Fallback to sync
            return self.query(sql, params)
        except Exception as ex:
            logging_config.save_log_ex(_tag, ex)
            return []
