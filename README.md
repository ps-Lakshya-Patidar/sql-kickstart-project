# dvdrental → Excel Exporter

A **production-ready Python project** that connects to the PostgreSQL `dvdrental`
sample database, executes 14 SQL exercises (Exercise 1–14), and exports every
result set into a single, beautifully formatted Excel workbook.

---

## Project Structure

```
SQL Kickstart Project/
│
├── config.py            # DB credentials, output path, shared logger
├── queries.py           # All SQL definitions — Q1–Q12 + Q13–Q15 special objects
├── db.py                # Database layer: get_connection(), execute_query()
├── excel_writer.py      # Excel layer: write_sheet(), autofit_columns(), create_summary_sheet()
├── main.py              # Pipeline orchestrator — entry point
│
├── export_queries.py    # Backward-compat shim → delegates to main.py
├── requirements.txt     # Python dependencies
├── sql_exercise_outputs.xlsx  # Generated on first run
├── export_queries.log   # Auto-generated log file
└── README.md
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `config.py` | Single source of truth for DB credentials, output filename, and the shared `logger` |
| `queries.py` | Pure data — all SQL strings for Exercise 1–14, zero imports |
| `db.py` | Database I/O — opens connections, executes SQL, measures timing |
| `excel_writer.py` | Excel I/O — styles, sheet creation, auto-fit, summary sheet |
| `main.py` | Orchestration — wires the other modules together, handles errors |

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11 + |
| PostgreSQL | 12 + |
| dvdrental database | loaded into PostgreSQL |

### Load dvdrental (if not already loaded)

1. Download the backup from the [PostgreSQL Tutorial site](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/).
2. Create the database and restore:

```bash
createdb dvdrental
pg_restore -U postgres -d dvdrental dvdrental.tar
```

---

## Installation

```bash
# 1. Navigate to the project folder
cd "SQL Kickstart Project"

# 2. (Recommended) Create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

`config.py` is listed in `.gitignore` and is **never committed** — your password stays local.

**Step 1** — Copy the example template:
```bash
# Windows
copy config.example.py config.py

# macOS / Linux
cp config.example.py config.py
```

**Step 2** — Open `config.py` and fill in your password:
```python
DB_CONFIG: dict[str, Any] = {
    "host":     "localhost",
    "database": "dvdrental",
    "user":     "postgres",
    "password": "YOUR_ACTUAL_PASSWORD",   # ← change this
    "port":     5432,
}
```

---

## Running the Script

```bash
# Recommended entry point
python main.py

# Also works (backward-compat shim)
python export_queries.py
```

On success you will see console output like:

```
2026-07-14 18:45:01  INFO      ════════════════════════════════════════════════════
2026-07-14 18:45:01  INFO      dvdrental  →  Excel Export  |  START
2026-07-14 18:45:01  INFO      Connecting to PostgreSQL  →  postgres@localhost:5432/dvdrental
2026-07-14 18:45:01  INFO      Connection established successfully.
2026-07-14 18:45:01  INFO      [Q1]  Executing query …
2026-07-14 18:45:01  INFO      [Q1]  ✓  10 row(s) returned  |  0.0154 s
...
2026-07-14 18:45:03  INFO      Workbook saved  →  sql_exercise_outputs.xlsx
2026-07-14 18:45:03  INFO      Done  |  15 succeeded / 0 failed  |  Total: 15 queries
```

---

## Output: sql_exercise_outputs.xlsx

The workbook contains **14 sheets** — one per exercise plus a **Summary** sheet
inserted at the front.

| Sheet | Content |
|-------|---------|
| **Summary** | Exercise · Rows Returned · Execution Time · Status (colour-coded) |
| **Exercise 1** | Film titles with daily rental price |
| **Exercise 2** | Films starting with 'A' between 60–120 minutes |
| **Exercise 3** | Film count grouped by rating |
| **Exercise 4** | Categories with more than 65 films |
| **Exercise 5** | Each film with its category name |
| **Exercise 6** | Customer full name and email domain |
| **Exercise 7** | Combined list of all actors and staff (UNION) |
| **Exercise 8** | Film count bucketed by length (short / medium / long) |
| **Exercise 9** | Customers whose total spend is above the average (CTE) |
| **Exercise 10** | Films priced above the average rental rate (subquery) |
| **Exercise 11** | Films ranked by rentals within each category (RANK) |
| **Exercise 12** | Comedy films from the film_catalog view |
| **Exercise 13** | Top 5 categories by revenue (materialized view) |
| **Exercise 14** | Top 10 most rented films (temporary table) |

### Excel Formatting

- **Bold, dark-navy header row** with white text
- **Alternating row fill** (light blue) for readability
- **Frozen header row** so headers stay visible while scrolling
- **Auto-fitted column widths** (capped at 60 characters)
- **Colour-coded Summary** — green = SUCCESS, red = FAILED, orange = SKIPPED

---

## Query Reference

### Standard Queries (Exercise 1–11)
Defined in `queries.py` — plain `SELECT` statements, executed directly.

### Special Queries (Exercise 12–14)
Also defined in `queries.py`, under `special_queries`.

| Exercise | Object Type | DDL Behaviour |
|----------|-------------|---------------|
| Exercise 12 | View | `CREATE OR REPLACE VIEW film_catalog …` then `SELECT` |
| Exercise 13 | Materialized View | `DROP … IF EXISTS category_revenue` → `CREATE MATERIALIZED VIEW …` → `SELECT` |
| Exercise 14 | Temporary Table | `CREATE TEMPORARY TABLE temp_rent …` then `SELECT` |

---

## Logging

Execution details are written to both the console and `export_queries.log`:

- Query execution start and completion
- Row count per query
- Execution time (seconds)
- Any errors with full tracebacks

---

## Error Handling

- Individual query failures are **caught and logged** without halting remaining queries.
- Failed queries appear in the Summary sheet with status **FAILED** (red).
- A database connection failure exits early with a critical-level log message.

---

## Dependencies

```
psycopg2-binary   # PostgreSQL adapter for Python
openpyxl          # Excel (.xlsx) read/write library
```

---

## License

MIT — free to use and adapt for personal or commercial projects.
