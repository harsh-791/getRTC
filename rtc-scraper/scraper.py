from playwright.sync_api import sync_playwright, expect
import time
import os
import re
import logging
from datetime import datetime
from db_handler import DBHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RTCScraper')

class RTCScraper:
    def __init__(self, db_handler=None):
        self.base_url = "https://landrecords.karnataka.gov.in/Service2/"
        self.db_handler = db_handler or DBHandler()  # Initialize DBHandler if not provided
        
    def _extract_year_from_period(self, period_text):
        """Extract the year from period text"""
        # First try to match the year pattern in parentheses
        match = re.search(r'\((\d{4}-\d{4}|\d{4}-\d{2})\s*\)', period_text)
        if match:
            year = match.group(1)
            # If it's in format 2020-21, convert to 2020-2021
            if len(year) < 9:  # Less than YYYY-YYYY
                start_year = year[:4]
                end_year = start_year[:2] + year[-2:]
                return f"{start_year}-{end_year}"
            return year
        return None

    def _is_year_in_range(self, year_text):
        """Check if the year is within 2012-13 to 2020-21 range"""
        try:
            # Convert year text (e.g., "2012-2013") to start year
            if not year_text:
                return False
                
            # Handle both formats: "2012-13" and "2012-2013"
            parts = year_text.split('-')
            if len(parts) != 2:
                return False
                
            # Get start year
            start_year = int(parts[0])
            return 2012 <= start_year <= 2020
        except:
            return False
            
    def scrape_documents(self, property_data):
        """
        Scrape RTC documents for all periods within the target year range (2012-13 to 2020-21)
        """
        try:
            # First insert property data and get property_id
            property_id = self.db_handler.insert_property(property_data)
            logger.info(f"Inserted property with ID: {property_id}")
            
            with sync_playwright() as p:
                # Launch the browser in visible mode with slower animations
                browser = p.chromium.launch(
                    headless=False,  # Show the browser window
                    slow_mo=500  # Add 500ms delay between actions
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080}  # Set viewport for better quality screenshots
                )
                page = context.new_page()
                
                try:
                    logger.info("Starting RTC document scraping with robust approach...")
                    # Navigate to the website
                    page.goto(self.base_url)
                    
                    # Click on "Old Year" button
                    page.get_by_role("button", name="Old Year").click()
                    
                    # Select District (Bangalore Rural = "21")
                    page.locator("#ctl00_MainContent_ddlODist").select_option("21")
                    
                    # Select Taluk (Devenahalli = "3")
                    page.locator("#ctl00_MainContent_ddlOTaluk").select_option("3")
                    
                    # Select Hobli (Kasaba = "2")
                    page.locator("#ctl00_MainContent_ddlOHobli").select_option("2")
                    
                    # Select Village (Devanahalli = "27")
                    page.locator("#ctl00_MainContent_ddlOVillage").select_option("27")
                    
                    # Enter Survey Number
                    page.get_by_placeholder("Survey Number").click()
                    page.get_by_placeholder("Survey Number").fill("22")
                    
                    # Click Go button
                    page.get_by_role("button", name="Go").click()
                    
                    # Click Go button again (as in your working script)
                    page.get_by_role("button", name="Go").click()
                    
                    # Select Surnoc ("*")
                    page.locator("#ctl00_MainContent_ddlOSurnocNo").select_option("*")
                    
                    # Select Hissa ("53" as in your working script, not "1" from property_data)
                    page.locator("#ctl00_MainContent_ddlOHissaNo").select_option("53")
                    
                    # Create a folder to save screenshots if it doesn't exist
                    screenshot_folder = os.path.join(os.path.dirname(__file__), 'screenshots')
                    os.makedirs(screenshot_folder, exist_ok=True)
                    
                    # Get all available periods
                    period_dropdown = page.locator("#ctl00_MainContent_ddlOPeriod")
                    period_options = period_dropdown.evaluate("""select => {
                        return Array.from(select.options).map(option => ({
                            value: option.value,
                            text: option.text
                        })).filter(option => option.value !== '0');
                    }""")
                    
                    logger.info(f"Found {len(period_options)} periods: {period_options}")
                    
                    # Process each period
                    documents = []
                    for period_option in period_options:
                        period_value = period_option['value']
                        period_text = period_option['text']
                        
                        try:
                            # Extract year from period text
                            target_year = self._extract_year_from_period(period_text)
                            
                            if not target_year:
                                logger.info(f"Could not extract year from period: {period_text}, skipping")
                                continue
                                
                            # Check if year is in our target range
                            if not self._is_year_in_range(target_year):
                                logger.info(f"Period {period_text} ({target_year}) is outside target range, skipping")
                                continue
                                
                            logger.info(f"Processing period: {period_text} ({target_year})")
                            
                            # Select the period
                            page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period_value)
                            time.sleep(1)
                            
                            # Get available years for this period
                            year_dropdown = page.locator("#ctl00_MainContent_ddlOYear")
                            year_options = year_dropdown.evaluate("""select => {
                                return Array.from(select.options).map(option => ({
                                    value: option.value,
                                    text: option.text
                                })).filter(option => option.value !== '0');
                            }""")
                            
                            logger.info(f"Available years for period {period_text}: {year_options}")
                            
                            if not year_options:
                                logger.warning(f"No year options found for period {period_text}")
                                continue
                                
                            # Try to find the matching year option
                            matching_year = next((year for year in year_options if year['text'] == target_year), None)
                            
                            # If no exact match, try a more flexible approach
                            if not matching_year and year_options:
                                logger.info(f"No exact match for year {target_year}, using first available year")
                                matching_year = year_options[0]
                                
                            if not matching_year:
                                logger.warning(f"Could not find matching year for period {period_text}")
                                continue
                                
                            # Select the year
                            page.locator("#ctl00_MainContent_ddlOYear").select_option(matching_year['value'])
                            time.sleep(1)
                            
                            # Click Fetch details
                            page.get_by_role("button", name="Fetch details").click()
                            time.sleep(1)
                            
                            # Check if View button is available
                            view_button = page.get_by_role("button", name="View")
                            if not view_button.is_visible():
                                logger.warning(f"View button not available for period {period_text}")
                                continue
                                
                            # Click View and handle popup
                            with page.expect_popup() as popup_info:
                                view_button.click()
                            popup_page = popup_info.value
                            
                            # Wait for popup content and image to load
                            popup_page.wait_for_load_state("networkidle")
                            popup_page.wait_for_selector("#ImgSketchPage")
                            time.sleep(2)  # Additional wait for image to render completely
                            
                            # Generate a clean filename
                            clean_period = re.sub(r'[^\w\-]', '_', period_text)
                            screenshot_path = os.path.join(screenshot_folder, f"RTC_{clean_period}_{matching_year['text']}.png")
                            
                            # Save the screenshot locally
                            popup_page.screenshot(path=screenshot_path)
                            logger.info(f"Screenshot saved locally at: {screenshot_path}")
                            
                            # After saving screenshot locally, store in database
                            doc_data = {
                                'period': period_value,
                                'period_text': period_text,
                                'year': matching_year['value'],
                                'year_text': matching_year['text'],
                                'screenshot_path': screenshot_path
                            }
                            
                            # Insert document into database
                            doc_id = self.db_handler.insert_document(property_id, doc_data)
                            logger.info(f"Inserted document with ID: {doc_id}")
                            
                            documents.append(doc_data)
                            
                            # Close popup
                            popup_page.close()
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Error processing period {period_text}: {str(e)}")
                            continue
                    
                    logger.info(f"Successfully processed {len(documents)} documents")
                    return documents
                    
                except Exception as e:
                    logger.error(f"Error during scraping: {str(e)}")
                    return None
                    
                finally:
                    if self.db_handler:
                        try:
                            self.db_handler.close()
                        except:
                            pass
                    context.close()
                    browser.close()

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return None
            
        finally:
            try:
                self.db_handler.close()
            except:
                pass

# Example usage:
if __name__ == "__main__":
    property_data = {
        'survey_number': '22',
        'surnoc': '*',
        'hissa': '53',  # Changed from "1" to "53" to match working script
        'village': 'Devanahalli',
        'hobli': 'Kasaba',
        'taluk': 'Devenahalli',
        'district': 'Bangalore Rural'
    }
    
    # Create DBHandler instance with new credentials
    db_handler = DBHandler(
        dbname="rtc_documents",
        user="rtc_user",
        password="rtc_password",
        host="localhost",
        port="5432"
    )
    
    # Initialize scraper with db_handler
    scraper = RTCScraper(db_handler)
    
    # Scrape documents
    documents = scraper.scrape_documents(property_data)
    print(f"Documents captured: {len(documents) if documents else 0}")
    
    if documents:
        print("\nStored documents:")
        # Retrieve documents from database to verify
        stored_docs = db_handler.get_property_documents(1)  # Assuming first property
        for doc in stored_docs:
            print(f"ID: {doc['id']}, Period: {doc['period_text']}, Year: {doc['year_text']}")
