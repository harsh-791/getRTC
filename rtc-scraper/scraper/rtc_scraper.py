from playwright.sync_api import sync_playwright
from db.database_handler import DatabaseHandler
from utils.logger import logger
import time

class RTCScraper:
    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler
        self.base_url = "https://landrecords.karnataka.gov.in/Service2/"

    def scrape_documents(self, property_data: dict):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            try:
                page.goto(self.base_url)
                page.get_by_role("button", name="Old Year").click()
                # Fill in the form
                page.locator("#ctl00_MainContent_ddlODist").select_option("21")
                time.sleep(2)
                page.locator("#ctl00_MainContent_ddlOTaluk").select_option("3")
                time.sleep(2)
                page.locator("#ctl00_MainContent_ddlOHobli").select_option("2")
                time.sleep(2)
                page.locator("#ctl00_MainContent_ddlOVillage").select_option("27")
                time.sleep(2)
                page.get_by_placeholder("Survey Number").fill("22")
                # Ensure the Go button is clicked twice as required
                page.get_by_role("button", name="Go").click()
                time.sleep(2)  # Wait for server response
                page.get_by_role("button", name="Go").click()
                time.sleep(2)  # Wait for server response

                # Process periods
                period_dropdown = page.locator("#ctl00_MainContent_ddlOPeriod")
                period_options = period_dropdown.evaluate(
                    """select => Array.from(select.options).map(option => ({
                        value: option.value,
                        text: option.text
                    })).filter(option => option.value !== '0');"""
                )

                for period_option in period_options:
                    period = period_option["value"]
                    period_text = period_option["text"]
                    # Insert logic for processing periods and years
                    # Save screenshots to the database
                    try:
                        page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period)
                        time.sleep(2)

                        # Wait for year dropdown to be enabled
                        page.wait_for_selector("#ctl00_MainContent_ddlOYear:not([disabled])")

                        # Get available years for this period
                        year_dropdown = page.locator("#ctl00_MainContent_ddlOYear")
                        year_options = year_dropdown.evaluate(
                            """select => Array.from(select.options).map(option => ({
                                value: option.value,
                                text: option.text
                            })).filter(option => option.value !== '0');"""
                        )

                        for year_option in year_options:
                            year = year_option["value"]
                            year_text = year_option["text"]

                            # Select year
                            page.locator("#ctl00_MainContent_ddlOYear").select_option(year)
                            time.sleep(2)

                            # Wait for Fetch details button to be enabled
                            page.wait_for_selector("#ctl00_MainContent_btnOFetchDetails:not([disabled])")

                            # Click Fetch details
                            fetch_button = page.get_by_role("button", name="Fetch details")
                            fetch_button.click()
                            time.sleep(2)

                            # Wait for View button
                            view_button = page.get_by_role("button", name="View")
                            view_button.wait_for(state="visible")

                            # Click View and handle popup
                            with page.expect_popup() as page1_info:
                                view_button.click()
                            page1 = page1_info.value

                            # Wait for popup content and image to load
                            page1.wait_for_load_state("networkidle")
                            page1.wait_for_selector("#ImgSketchPage")
                            time.sleep(2)  # Additional wait for image to render completely

                            # Take a screenshot and save to the database
                            screenshot_bytes = page1.screenshot()
                            self.db_handler.insert_screenshot(period_text, year_text, screenshot_bytes)
                            logger.info(f"Screenshot for {period_text} ({year_text}) saved to the database.")

                            # Close popup
                            page1.close()
                            time.sleep(2)

                    except Exception as e:
                        logger.error(f"Error processing period {period_text}: {e}")

            except Exception as e:
                logger.error(f"Error during scraping: {e}")
            finally:
                context.close()
                browser.close()