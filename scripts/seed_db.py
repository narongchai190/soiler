#!/usr/bin/env python3
"""
Database Seeding Script for S.O.I.L.E.R.

Creates a fresh database with sample data from seed.json.
Safe to run on fresh installations.

Usage:
    python scripts/seed_db.py
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


def create_database(db_path: Path) -> None:
    """Create database with basic schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create analyses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            location TEXT,
            crop TEXT,
            ph REAL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            field_size_rai REAL,
            notes TEXT,
            created_at TEXT
        )
    """)

    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"✓ Created database: {db_path}")


def load_seed_data(seed_path: Path) -> dict:
    """Load seed data from JSON file."""
    with open(seed_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_database(db_path: Path, seed_data: dict) -> None:
    """Seed database with sample data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert sample analyses
    for analysis in seed_data.get("sample_analyses", []):
        cursor.execute("""
            INSERT OR REPLACE INTO analyses
            (id, location, crop, ph, nitrogen, phosphorus, potassium, field_size_rai, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis["id"],
            analysis["location"],
            analysis["crop"],
            analysis["ph"],
            analysis["nitrogen"],
            analysis["phosphorus"],
            analysis["potassium"],
            analysis["field_size_rai"],
            analysis.get("notes", ""),
            datetime.now().isoformat()
        ))

    # Insert default settings
    settings = seed_data.get("default_settings", {})
    for key, value in settings.items():
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, json.dumps(value)))

    conn.commit()
    conn.close()
    print(f"✓ Seeded {len(seed_data.get('sample_analyses', []))} sample analyses")
    print(f"✓ Seeded {len(settings)} default settings")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "soiler_v1.db"
    seed_path = project_root / "data" / "seed" / "seed.json"

    print("=" * 60)
    print("S.O.I.L.E.R. Database Seeder")
    print("=" * 60)

    if not seed_path.exists():
        print(f"ERROR: Seed file not found: {seed_path}")
        return 1

    # Check if DB already exists
    if db_path.exists():
        response = input(f"Database exists at {db_path}. Overwrite? [y/N]: ")
        if response.lower() != "y":
            print("Aborted.")
            return 0
        db_path.unlink()

    # Create and seed
    create_database(db_path)
    seed_data = load_seed_data(seed_path)
    seed_database(db_path, seed_data)

    print()
    print("✓ Database seeding complete!")
    print(f"  Location: {db_path}")
    return 0


if __name__ == "__main__":
    exit(main())
