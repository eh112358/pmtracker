"""
Database migration script to add missing tables.
Run this if you have existing data and don't want to delete the database.

Usage: python -m app.migrate_db
"""
from sqlalchemy import inspect, text
from .database import engine, Base
from . import models  # Import all models to register them

def migrate():
    """Add any missing tables to the database."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    print(f"Existing tables: {existing_tables}")

    # Get all model tables
    model_tables = Base.metadata.tables.keys()
    print(f"Model tables: {list(model_tables)}")

    # Create only missing tables
    missing_tables = set(model_tables) - set(existing_tables)

    if missing_tables:
        print(f"Creating missing tables: {missing_tables}")
        # Create all tables (create_all only creates missing ones)
        Base.metadata.create_all(bind=engine)
        print("Migration complete!")
    else:
        print("No missing tables. Database is up to date.")

if __name__ == "__main__":
    migrate()
