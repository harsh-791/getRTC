import os
import psycopg2
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class DatabaseHandler:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """Create a table to store screenshots if it doesn't exist"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS screenshots (
                id SERIAL PRIMARY KEY,
                period TEXT NOT NULL,
                year TEXT NOT NULL,
                screenshot BYTEA NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

    def insert_screenshot(self, period: str, year: str, screenshot_bytes: bytes) -> None:
        """Insert a screenshot into the database"""
        try:
            self.cursor.execute(
                """
                INSERT INTO screenshots (period, year, screenshot)
                VALUES (%s, %s, %s)
                """,
                (period, year, psycopg2.Binary(screenshot_bytes))
            )
            self.connection.commit()
        except Exception as e:
            raise RuntimeError(f"Error inserting screenshot: {e}")

    def get_screenshots(self) -> List[Dict[str, Any]]:
        """Retrieve all screenshots from the database"""
        self.cursor.execute("SELECT id, period, year, created_at FROM screenshots")
        rows = self.cursor.fetchall()
        return [
            {"id": row[0], "period": row[1], "year": row[2], "created_at": row[3]}
            for row in rows
        ]

    def close(self):
        """Close the database connection"""
        self.cursor.close()
        self.connection.close()