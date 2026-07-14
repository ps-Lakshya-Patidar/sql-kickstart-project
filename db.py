"""
db.py
=====
Database layer for the dvdrental → Excel export project.

Responsibilities
----------------
- get_connection()  : Opens and returns a psycopg2 connection.
- execute_query()   : Executes a single SELECT SQL and returns
                      (columns, rows, elapsed_seconds).

All database credentials are read from config.DB_CONFIG so this module
never hard-codes connection details.
"""

from __future__ import annotations

import time
from typing import Any

import psycopg2
import psycopg2.extensions

from config import DB_CONFIG, logger


# ──────────────────────────────────────────────────────────────────────────────
# CONNECTION
# ──────────────────────────────────────────────────────────────────────────────

def get_connection() -> psycopg2.extensions.connection:
    """
    Establish and return a psycopg2 connection to the dvdrental database.

    Reads connection parameters from ``config.DB_CONFIG``.
    Sets ``autocommit = True`` so every DDL statement (CREATE, DROP) commits
    immediately without requiring an explicit ``conn.commit()`` call.

    Returns
    -------
    psycopg2.extensions.connection
        An open, auto-committing database connection.

    Raises
    ------
    psycopg2.OperationalError
        If the database is unreachable or credentials are wrong.
    """
    logger.info(
        "Connecting to PostgreSQL  →  %s@%s:%s/%s",
        DB_CONFIG["user"],
        DB_CONFIG["host"],
        DB_CONFIG["port"],
        DB_CONFIG["database"],
    )
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    logger.info("Connection established successfully.")
    return conn


# ──────────────────────────────────────────────────────────────────────────────
# QUERY EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

def execute_query(
    cursor: psycopg2.extensions.cursor,
    label: str,
    sql: str,
) -> tuple[list[str], list[tuple[Any, ...]], float]:
    """
    Execute a single SQL SELECT statement and return its results.

    Parameters
    ----------
    cursor : psycopg2.extensions.cursor
        An open database cursor obtained from an active connection.
    label : str
        Human-readable identifier used in log messages (e.g. ``"Q1"``).
    sql : str
        The SQL statement to execute. Must be a SELECT (or equivalent
        statement that populates ``cursor.description`` after execution).

    Returns
    -------
    columns : list[str]
        Column names derived from ``cursor.description``.
    rows : list[tuple[Any, ...]]
        All result rows returned by the query.
    elapsed : float
        Wall-clock execution time in seconds.

    Raises
    ------
    psycopg2.DatabaseError
        Propagated from psycopg2 if the SQL is invalid or execution fails.
    """
    logger.info("[%s]  Executing query …", label)
    t0 = time.perf_counter()
    cursor.execute(sql)
    rows    = cursor.fetchall()
    elapsed = time.perf_counter() - t0
    columns = [desc[0] for desc in cursor.description]
    logger.info(
        "[%s]  ✓  %d row(s) returned  |  %.4f s",
        label, len(rows), elapsed,
    )
    return columns, rows, elapsed
