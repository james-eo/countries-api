#!/usr/bin/env python3
"""
Script to create database tables on Railway production database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.database import Base
from app.models.country import Country

# Load environment variables
load_dotenv()

def create_production_tables():
    """Create tables on the production database"""
    try:
        # Use Railway's MySQL environment variables
        mysql_host = os.getenv("MYSQLHOST")
        mysql_port = os.getenv("MYSQLPORT", "3306")
        mysql_user = os.getenv("MYSQLUSER")
        mysql_password = os.getenv("MYSQLPASSWORD")
        mysql_database = os.getenv("MYSQLDATABASE")
        
        if not all([mysql_host, mysql_user, mysql_password, mysql_database]):
            print("❌ Missing required environment variables")
            print(f"MYSQLHOST: {mysql_host}")
            print(f"MYSQLUSER: {mysql_user}")
            print(f"MYSQLDATABASE: {mysql_database}")
            return False
        
        # Create database URL
        database_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        print("🗄️ Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_production_tables()
    exit(0 if success else 1)