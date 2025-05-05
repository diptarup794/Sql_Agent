import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain_community.utilities.sql_database import SQLDatabase

def connect_to_db(db_path):
    """Connect to a SQLite database."""
    try:
        # Create SQLAlchemy engine
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # Create LangChain SQLDatabase object
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        return {
            "engine": engine,
            "db": db,
            "status": "success",
            "message": f"Successfully connected to {db_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to database: {str(e)}"
        }

def get_tables_info(db_path):
    """Get information about tables in the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        tables_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            tables_info[table_name] = [col[1] for col in columns]
        
        conn.close()
        return {
            "status": "success",
            "tables": tables_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting table information: {str(e)}"
        }