"""
Database initialization script
Run this to create all tables in the database
"""

from app.database import engine, Base
from app.models.country import Country


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    create_tables()