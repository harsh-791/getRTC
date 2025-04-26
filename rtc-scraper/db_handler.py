import psycopg2
import os
import base64
import logging
from datetime import datetime
from dotenv import load_dotenv
from api.models import RTCData, RTCDocument

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DBHandler')

class DBHandler:
    def __init__(self):
        self.conn = None
        self.connect()
        self.initialize_db()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'rtc_documents'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            logger.info(f"Connected to database: {os.getenv('DB_NAME', 'rtc_documents')}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    def initialize_db(self):
        """Initialize database and create required tables if they don't exist"""
        try:
            with self.conn.cursor() as cur:
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
                        period_value VARCHAR(50),
                        period_text TEXT,
                        year_value VARCHAR(50),
                        year_text VARCHAR(50),
                        screenshot_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def ensure_connection(self):
        if self.conn is None or self.conn.closed:
            self.connect()

    def insert_property(self, property_data):
        """Insert property details and return property_id"""
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
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
                self.conn.commit()
                return property_id
        except Exception as e:
            logger.error(f"Error inserting property: {str(e)}")
            raise

    def insert_document(self, property_id, document_data):
        """Insert RTC document details and screenshot path"""
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rtc_documents 
                    (property_id, period_value, period_text, year_value, year_text, screenshot_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    property_id,
                    document_data['period'],
                    document_data['period_text'],
                    document_data['year'],
                    document_data['year_text'],
                    document_data['screenshot_path']
                ))
                document_id = cur.fetchone()[0]
                self.conn.commit()
                return document_id
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            raise

    def get_property_documents(self, property_id):
        """Retrieve all documents for a given property"""
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM rtc_documents 
                    WHERE property_id = %s 
                    ORDER BY created_at DESC
                """, (property_id,))
                columns = [desc[0] for desc in cur.description]
                documents = [dict(zip(columns, row)) for row in cur.fetchall()]
                return documents
        except Exception as e:
            logger.error(f"Error getting property documents: {str(e)}")
            raise

    def get_document_by_id(self, document_id):
        """Retrieve a specific document by its ID"""
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM rtc_documents 
                    WHERE id = %s
                """, (document_id,))
                columns = [desc[0] for desc in cur.description]
                document = dict(zip(columns, cur.fetchone()))
                return document
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")