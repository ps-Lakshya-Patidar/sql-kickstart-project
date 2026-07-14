"""
export_queries.py
=================
Backward-compatibility shim.

The project has been refactored into separate modules:

    config.py        ← credentials, output path, shared logger
    queries.py       ← SQL definitions (Q1–Q15)
    db.py            ← get_connection(), execute_query()
    excel_writer.py  ← write_sheet(), autofit_columns(), create_summary_sheet()
    main.py          ← pipeline orchestration (entry point)

Running this file delegates directly to main.main() so existing scripts
or shortcuts that call  `python export_queries.py`  continue to work.
"""

from main import main

if __name__ == "__main__":
    main()
