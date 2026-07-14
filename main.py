"""
main.py
=======
Entry point for the dvdrental → Excel export pipeline.

Orchestration order
-------------------
1. Open a database connection  (db.get_connection)
2. Run Q1–Q12 standard queries (queries.queries)
3. Run Q13–Q15 special objects (queries.special_queries)
4. Write each result to its own Excel sheet (excel_writer.write_sheet)
5. Append a colour-coded Summary sheet (excel_writer.create_summary_sheet)
6. Save the workbook to config.OUTPUT_FILE

Run
---
    python main.py
"""

from __future__ import annotations

import time
from typing import Any

import psycopg2
from openpyxl import Workbook

from config import OUTPUT_FILE, logger
from db import execute_query, get_connection
from excel_writer import create_summary_sheet, write_sheet
from queries import queries, special_queries


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _blank_entry(label: str) -> dict[str, Any]:
    """Return a default (FAILED) summary entry for a given query label."""
    return {
        "question":       label,
        "rows_returned":  0,
        "execution_time": 0.0,
        "status":         "FAILED",
    }


# ──────────────────────────────────────────────────────────────────────────────
# PIPELINE STAGES
# ──────────────────────────────────────────────────────────────────────────────

def run_standard_queries(
    cursor: Any,
    wb: Workbook,
    summary: list[dict[str, Any]],
) -> None:
    """
    Execute Q1–Q12 (plain SELECT statements) and write each result to
    its own worksheet.

    Parameters
    ----------
    cursor : psycopg2.extensions.cursor
        An open database cursor.
    wb : openpyxl.Workbook
        The target workbook; one sheet is appended per query.
    summary : list[dict]
        Accumulated execution metadata; one entry is appended per query.
    """
    for label, sql in queries.items():
        entry = _blank_entry(label)
        try:
            columns, rows, elapsed = execute_query(cursor, label, sql)
            write_sheet(wb, label, columns, rows)
            entry["rows_returned"]  = len(rows)
            entry["execution_time"] = elapsed
            entry["status"]         = "SUCCESS"
        except Exception as exc:
            logger.error("[%s]  ✗  %s", label, exc, exc_info=True)
        finally:
            summary.append(entry)


def run_special_queries(
    cursor: Any,
    wb: Workbook,
    summary: list[dict[str, Any]],
) -> None:
    """
    Execute Q13–Q15 (temp table, view, materialized view) and write each
    result to its own worksheet.

    For each spec the function:
    - Drops the object first (materialized views only).
    - Executes the CREATE statement.
    - Executes the SELECT statement and captures results.

    Parameters
    ----------
    cursor : psycopg2.extensions.cursor
        An open database cursor.
    wb : openpyxl.Workbook
        The target workbook; one sheet is appended per query.
    summary : list[dict]
        Accumulated execution metadata; one entry is appended per query.
    """
    for label, spec in special_queries.items():
        entry = _blank_entry(label)
        try:
            obj_type = spec.get("type", "")
            logger.info("[%s]  Object type  →  %s", label, obj_type)

            t0 = time.perf_counter()

            # Drop before re-creating (materialized views only)
            if obj_type == "materialized_view" and "drop" in spec:
                logger.info("[%s]  Dropping existing materialized view …", label)
                cursor.execute(spec["drop"])

            # DDL — CREATE TEMP TABLE / VIEW / MATERIALIZED VIEW
            logger.info("[%s]  Executing CREATE statement …", label)
            cursor.execute(spec["create"])

            # DQL — SELECT results from the new object
            logger.info("[%s]  Executing SELECT statement …", label)
            cursor.execute(spec["select"])
            rows    = cursor.fetchall()
            elapsed = time.perf_counter() - t0
            columns = [desc[0] for desc in cursor.description]

            logger.info(
                "[%s]  ✓  %d row(s) returned  |  %.4f s",
                label, len(rows), elapsed,
            )
            write_sheet(wb, label, columns, rows)
            entry["rows_returned"]  = len(rows)
            entry["execution_time"] = elapsed
            entry["status"]         = "SUCCESS"

        except Exception as exc:
            logger.error("[%s]  ✗  %s", label, exc, exc_info=True)
        finally:
            summary.append(entry)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Orchestrate the end-to-end dvdrental → Excel export pipeline.

    Steps
    -----
    1. Open a database connection.
    2. Execute Q1–Q12 (standard queries).
    3. Execute Q13–Q15 (special objects).
    4. Build the Summary sheet.
    5. Save the workbook.
    6. Log overall statistics.
    """
    logger.info("═" * 60)
    logger.info("dvdrental  →  Excel Export  |  START")
    logger.info("═" * 60)

    conn: psycopg2.extensions.connection | None = None
    wb   = Workbook()
    wb.remove(wb.active)          # discard the default blank sheet

    summary_data: list[dict[str, Any]] = []

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        run_standard_queries(cursor, wb, summary_data)
        run_special_queries(cursor, wb, summary_data)

        create_summary_sheet(wb, summary_data)

        wb.save(OUTPUT_FILE)
        logger.info("═" * 60)
        logger.info("Workbook saved  →  %s", OUTPUT_FILE)
        logger.info("═" * 60)

    except psycopg2.OperationalError as exc:
        logger.critical("Cannot connect to the database: %s", exc)
        raise SystemExit(1) from exc

    finally:
        if conn is not None:
            conn.close()
            logger.info("Database connection closed.")

    # ── Final statistics ──────────────────────────────────────────────────────
    success = sum(1 for e in summary_data if e["status"] == "SUCCESS")
    failed  = sum(1 for e in summary_data if e["status"] == "FAILED")
    logger.info(
        "Done  |  %d succeeded  /  %d failed  |  Total: %d queries",
        success, failed, len(summary_data),
    )


if __name__ == "__main__":
    main()
