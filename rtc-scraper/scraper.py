from playwright.async_api import async_playwright, expect
import time
import os
import re
import logging
from datetime import datetime
from db_handler import DBHandler
from dotenv import load_dotenv
import traceback
import asyncio
from api.models import RTCData, RTCDocument
from asgiref.sync import sync_to_async

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
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
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
            
    async def scrape_documents(self, property_data):
        """
        Scrape RTC documents for all periods within the target year range (2012-13 to 2020-21)
        """
        try:
            # Create RTCData object for the property using sync_to_async
            rtc_data = await sync_to_async(RTCData.objects.create)(
                survey_number=property_data['survey_number'],
                surnoc=property_data['surnoc'],
                hissa=property_data['hissa'],
                village=property_data['village'],
                hobli=property_data['hobli'],
                taluk=property_data['taluk'],
                district=property_data['district'],
            )
            logger.info(f"Created RTCData with ID: {rtc_data.id}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,  # Show the browser window
                    slow_mo=500  # Add 500ms delay between actions
                )
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},  # Set viewport for better quality screenshots
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                page = await context.new_page()
                
                try:
                    logger.info("Starting RTC document scraping with robust approach...")
                    # Navigate to the website and wait for it to load
                    await page.goto(self.base_url, wait_until='networkidle')
                    await asyncio.sleep(2)  # Additional wait for page to stabilize
                    
                    # Click on "Old Year" button
                    old_year_button = page.get_by_role("button", name="Old Year")
                    await old_year_button.wait_for(state="visible")
                    await old_year_button.click()
                    await asyncio.sleep(1)
                    
                    # Select District (Bangalore Rural = "21")
                    await page.locator("#ctl00_MainContent_ddlODist").select_option("21")
                    await asyncio.sleep(1)
                    
                    # Select Taluk (Devenahalli = "3")
                    await page.locator("#ctl00_MainContent_ddlOTaluk").select_option("3")
                    await asyncio.sleep(1)
                    
                    # Select Hobli (Kasaba = "2")
                    await page.locator("#ctl00_MainContent_ddlOHobli").select_option("2")
                    await asyncio.sleep(1)
                    
                    # Select Village (Devanahalli = "27")
                    await page.locator("#ctl00_MainContent_ddlOVillage").select_option("27")
                    await asyncio.sleep(1)
                    
                    # Enter Survey Number
                    survey_input = page.get_by_placeholder("Survey Number")
                    await survey_input.wait_for(state="visible")
                    await survey_input.fill("22")
                    await asyncio.sleep(1)
                    
                    # Click Go button
                    go_button = page.get_by_role("button", name="Go")
                    await go_button.wait_for(state="visible")
                    await go_button.click()
                    await asyncio.sleep(2)
                    
                    # Click Go button again (as in your working script)
                    await go_button.click()
                    await asyncio.sleep(2)
                    
                    # Select Surnoc ("*")
                    await page.locator("#ctl00_MainContent_ddlOSurnocNo").select_option("*")
                    await asyncio.sleep(1)
                    
                    # Select Hissa ("53" as in your working script, not "1" from property_data)
                    await page.locator("#ctl00_MainContent_ddlOHissaNo").select_option("53")
                    await asyncio.sleep(1)
                    
                    # Get all available periods
                    period_dropdown = page.locator("#ctl00_MainContent_ddlOPeriod")
                    await period_dropdown.wait_for(state="visible")
                    period_options = await period_dropdown.evaluate("""select => {
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
                            await page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period_value)
                            await asyncio.sleep(2)
                            
                            # Get available years for this period
                            year_dropdown = page.locator("#ctl00_MainContent_ddlOYear")
                            await year_dropdown.wait_for(state="visible")
                            year_options = await year_dropdown.evaluate("""select => {
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
                            await page.locator("#ctl00_MainContent_ddlOYear").select_option(matching_year['value'])
                            await asyncio.sleep(2)
                            
                            # Click Fetch details
                            fetch_button = page.get_by_role("button", name="Fetch details")
                            await fetch_button.wait_for(state="visible")
                            await fetch_button.click()
                            await asyncio.sleep(2)
                            
                            # Check if View button is available
                            view_button = page.get_by_role("button", name="View")
                            if not await view_button.is_visible():
                                logger.warning(f"View button not available for period {period_text}")
                                continue
                                
                            # Click View and handle popup
                            try:
                                # Wait for the View button to be clickable
                                await view_button.wait_for(state="visible")
                                is_enabled = await view_button.is_enabled()
                                if not is_enabled:
                                    logger.warning("View button is not enabled, skipping.")
                                    continue
                                
                                # Click View and wait for popup with increased timeout
                                async with page.expect_popup(timeout=120000) as popup_info:  # Increased timeout to 2 minutes
                                    await view_button.click()
                                    
                                popup_page = await popup_info.value
                                
                                # Wait for popup content and image to load with increased timeout
                                await popup_page.wait_for_load_state("networkidle", timeout=120000)
                                await popup_page.wait_for_selector("#ImgSketchPage", timeout=120000)
                                
                                # Additional wait for image to render completely
                                await asyncio.sleep(5)  # Increased wait time
                                
                                # Generate a clean filename
                                clean_period = re.sub(r'[\w\-]', '_', period_text)
                                screenshot_filename = f"RTC_{clean_period}_{matching_year['text']}.png"
                                screenshot_path = os.path.join(self.screenshots_dir, screenshot_filename)
                                
                                # Save the screenshot locally with retry logic
                                max_retries = 3
                                for attempt in range(max_retries):
                                    try:
                                        await popup_page.screenshot(path=screenshot_path)
                                        logger.info(f"Screenshot saved locally at: {screenshot_path}")
                                        break
                                    except Exception as e:
                                        if attempt == max_retries - 1:
                                            raise
                                        logger.warning(f"Attempt {attempt + 1} failed to save screenshot, retrying...")
                                        await asyncio.sleep(2)
                                
                                # Save this relative path in the DB for Django/Frontend
                                relative_screenshot_path = os.path.join('screenshots', screenshot_filename)
                                doc = await sync_to_async(RTCDocument.objects.create)(
                                    rtc_data=rtc_data,
                                    period=period_value,
                                    period_text=period_text,
                                    year=matching_year['value'],
                                    year_text=matching_year['text'],
                                    screenshot_path=relative_screenshot_path
                                )
                                logger.info(f"Inserted RTCDocument with ID: {doc.id}")
                                documents.append({
                                    'id': doc.id,
                                    'period': doc.period,
                                    'period_text': doc.period_text,
                                    'year': doc.year,
                                    'year_text': doc.year_text,
                                    'screenshot_path': doc.screenshot_path
                                })
                                
                                # Close popup
                                await popup_page.close()
                                await asyncio.sleep(2)  # Increased wait time after closing popup
                                
                            except Exception as e:
                                logger.error(f"Error handling popup for period {period_text}: {str(e)}")
                                logger.error(f"Traceback: {traceback.format_exc()}")
                                continue
                                
                        except Exception as e:
                            logger.error(f"Error processing period {period_text}: {str(e)}")
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            continue
                    
                    logger.info(f"Successfully processed {len(documents)} documents")
                    return documents
                    
                except Exception as e:
                    logger.error(f"Error during scraping: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return None
                    
                finally:
                    if self.db_handler:
                        try:
                            self.db_handler.close()
                        except:
                            pass
                    await context.close()
                    await browser.close()

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
    
    # Create DBHandler instance with environment variables
    db_handler = DBHandler()
    
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
