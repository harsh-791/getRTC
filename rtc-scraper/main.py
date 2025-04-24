import sys
import os

# Ensure the rtc-scraper directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database_handler import DatabaseHandler
from scraper.rtc_scraper import RTCScraper

if __name__ == "__main__":
    db_handler = DatabaseHandler()
    scraper = RTCScraper(db_handler)

    property_data = {
        "survey_number": "22",
        "surnoc": "*",
        "hissa": "1",
        "village": "Devanahalli",
        "hobli": "Kasaba",
        "taluk": "Devenahalli",
        "district": "Bangalore Rural"
    }

    scraper.scrape_documents(property_data)
    db_handler.close()