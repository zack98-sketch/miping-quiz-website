#!/usr/bin/env python3
"""CLI tool to import questions from Excel file."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal
from app.importers.excel_importer import import_excel


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_cli.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    print("Initializing database...")
    init_db()
    
    print(f"Importing from: {file_path}")
    db = SessionLocal()
    try:
        result = import_excel(file_path, db)
        print(f"\nImport completed!")
        print(f"  Total: {result['total']}")
        print(f"  Success: {result['success']}")
        print(f"  Errors: {result['errors']}")
        if result['error_details']:
            print(f"\nError details (first 10):")
            for err in result['error_details'][:10]:
                print(f"  Row {err['row']}: {err['error']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
