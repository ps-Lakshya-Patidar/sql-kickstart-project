"""
config.example.py
=================
Template for database configuration.

SETUP INSTRUCTIONS
------------------
1. Copy this file and rename it to config.py:
       cp config.example.py config.py          (macOS / Linux)
       copy config.example.py config.py        (Windows)

2. Fill in your actual PostgreSQL credentials in config.py.

3. config.py is listed in .gitignore and will NEVER be committed.
   Only config.example.py (this file) is tracked by git.
"""

from __future__ import annotations

import logging
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# DATABASE  –  fill in your real values in config.py (not here)
# ──────────────────────────────────────────────────────────────────────────────
DB_CONFIG: dict[str, Any] = {
    "host":     "localhost",
    "database": "dvdrental",
    "user":     "postgres",
    "password": "YOUR_PASSWORD_HERE",   # ← replace in config.py
    "port":     5432,
}

# ──────────────────────────────────────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────────────────────────────────────
OUTPUT_FILE: str = "sql_exercise_outputs.xlsx"
LOG_FILE:    str = "export_queries.log"

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)

logger: logging.Logger = logging.getLogger("dvdrental_export")
