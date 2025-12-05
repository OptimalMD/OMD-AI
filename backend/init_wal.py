#!/usr/bin/env python3
"""
Initialize SQLite database with WAL mode and proper settings.
This script should be run when the database is not being accessed by other processes.
"""

import sqlite3
import os
from pathlib import Path

# Get the database path
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "webui.db"

print(f"Initializing database at: {DB_PATH}")

if not DB_PATH.exists():
    print(f"Error: Database file not found at {DB_PATH}")
    exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    cursor = conn.cursor()
    
    # Set WAL mode
    print("Setting journal mode to WAL...")
    cursor.execute("PRAGMA journal_mode=WAL")
    result = cursor.fetchone()
    print(f"Journal mode: {result[0]}")
    
    # Set busy timeout
    print("Setting busy timeout to 30 seconds...")
    cursor.execute("PRAGMA busy_timeout=30000")
    
    # Set synchronous mode to NORMAL for better performance with WAL
    print("Setting synchronous mode to NORMAL...")
    cursor.execute("PRAGMA synchronous=NORMAL")
    
    # Set WAL autocheckpoint
    print("Setting WAL autocheckpoint to 1000 pages...")
    cursor.execute("PRAGMA wal_autocheckpoint=1000")
    
    # Verify settings
    print("\nVerifying settings:")
    cursor.execute("PRAGMA journal_mode")
    print(f"  journal_mode: {cursor.fetchone()[0]}")
    
    cursor.execute("PRAGMA synchronous")
    print(f"  synchronous: {cursor.fetchone()[0]}")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\nDatabase initialized successfully!")
    print("WAL mode is now enabled and the database is ready for concurrent access.")
    
except sqlite3.Error as e:
    print(f"Error: {e}")
    exit(1)
