import psycopg2
import os
import base64
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DBHandler')

class DBHandler:
    def __init__(self, dbname="rtc_documents", user="postgres", password="postgres", host="localhost", port="5432"):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.conn = None
        self.initialize_db()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            return self.conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    def initialize_db(self):
        """Initialize database and create required tables if they don't exist"""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                # Create properties table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS properties (
                        id SERIAL PRIMARY KEY,
                        survey_number VARCHAR(50),
                        surnoc VARCHAR(50),
                        hissa VARCHAR(50),
                        village VARCHAR(100),
                        hobli VARCHAR(100),
                        taluk VARCHAR(100),
                        district VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create documents table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS rtc_documents (
                        id SERIAL PRIMARY KEY,
                        property_id INTEGER REFERENCES properties(id),
                        period_value VARCHAR(100),
                        period_text VARCHAR(200),
                        year_value VARCHAR(100),
                        year_text VARCHAR(100),
                        image_data BYTEA,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(property_id, period_value, year_value)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_property(self, property_data):
        """Insert property details and return property_id"""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO properties 
                    (survey_number, surnoc, hissa, village, hobli, taluk, district)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    property_data['survey_number'],
                    property_data['surnoc'],
                    property_data['hissa'],
                    property_data['village'],
                    property_data['hobli'],
                    property_data['taluk'],
                    property_data['district']
                ))
                property_id = cur.fetchone()[0]
                conn.commit()
                return property_id
        except Exception as e:
            logger.error(f"Error inserting property: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_document(self, property_id, document_data):
        """Insert RTC document details and image"""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                # Read image file and convert to binary
                with open(document_data['screenshot_path'], 'rb') as img_file:
                    img_data = img_file.read()

                cur.execute("""
                    INSERT INTO rtc_documents 
                    (property_id, period_value, period_text, year_value, year_text, image_data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (property_id, period_value, year_value) 
                    DO UPDATE SET 
                        image_data = EXCLUDED.image_data,
                        period_text = EXCLUDED.period_text,
                        year_text = EXCLUDED.year_text
                    RETURNING id
                """, (
                    property_id,
                    document_data['period'],
                    document_data['period_text'],
                    document_data['year'],
                    document_data['year_text'],
                    psycopg2.Binary(img_data)
                ))
                document_id = cur.fetchone()[0]
                conn.commit()
                return document_id
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_property_documents(self, property_id):
        """Retrieve all documents for a given property"""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, period_text, year_text, image_data 
                    FROM rtc_documents 
                    WHERE property_id = %s
                    ORDER BY year_text
                """, (property_id,))
                documents = []
                for doc_id, period_text, year_text, image_data in cur.fetchall():
                    documents.append({
                        'id': doc_id,
                        'period_text': period_text,
                        'year_text': year_text,
                        'image_data': image_data
                    })
                return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_document_by_id(self, document_id):
        """Retrieve a specific document by its ID"""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, period_text, year_text, image_data 
                    FROM rtc_documents 
                    WHERE id = %s
                """, (document_id,))
                result = cur.fetchone()
                if result:
                    doc_id, period_text, year_text, image_data = result
                    return {
                        'id': doc_id,
                        'period_text': period_text,
                        'year_text': year_text,
                        'image_data': image_data
                    }
                return None
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()