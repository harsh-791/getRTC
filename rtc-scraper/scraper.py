from playwright.sync_api import sync_playwright, expect
import time
import os
from datetime import datetime
import re
from urllib.parse import unquote
import base64
import requests

class RTCScraper:
    def __init__(self):
        self.base_url = "https://landrecords.karnataka.gov.in/Service2/"
        
    def _extract_image_url(self, content):
        """Extract image URL from document content"""
        match = re.search(r'src="(https://landrecords\.karnataka\.gov\.in/service2images//RTCPreviewPng/[^"]+)"', content)
        return unquote(match.group(1)) if match else None

    def _download_image(self, url, save_path):
        """Download image from URL and save to path without any processing"""
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': self.base_url
            }
            
            # Make request with headers and stream the response
            response = requests.get(url, headers=headers, verify=False, stream=True)
            response.raise_for_status()
            
            # Write the raw bytes directly to file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return False

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
            start_year = int(year_text.split('-')[0])
            return 2012 <= start_year <= 2020
        except:
            return False

    def scrape_documents(self, property_data):
        """
        Scrape RTC documents for the given property
        """
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
                # Navigate to the website
                page.goto(self.base_url)
                
                # Click on "Old Year" button
                page.get_by_role("button", name="Old Year").click()
                
                # Wait for district dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlODist:not([disabled])")
                
                # Select District (Bangalore Rural = "21")
                page.locator("#ctl00_MainContent_ddlODist").select_option("21")
                time.sleep(2)  # Wait for server response
                
                # Wait for taluk dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOTaluk:not([disabled])")
                
                # Select Taluk (Devenahalli = "3")
                page.locator("#ctl00_MainContent_ddlOTaluk").select_option("3")
                time.sleep(2)  # Wait for server response
                
                # Wait for hobli dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOHobli:not([disabled])")
                
                # Select Hobli (Kasaba = "2")
                page.locator("#ctl00_MainContent_ddlOHobli").select_option("2")
                time.sleep(2)  # Wait for server response
                
                # Wait for village dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOVillage:not([disabled])")
                
                # Select Village (Devanahalli = "27")
                page.locator("#ctl00_MainContent_ddlOVillage").select_option("27")
                time.sleep(2)  # Wait for server response
                
                # Enter Survey Number
                survey_input = page.get_by_placeholder("Survey Number")
                survey_input.click()
                survey_input.fill("22")
                page.get_by_role("button", name="Go").click()
                time.sleep(2)  # Wait for server response
                
                # Sometimes need to click Go twice
                page.get_by_role("button", name="Go").click()
                time.sleep(2)  # Wait for server response
                
                # Wait for Surnoc dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOSurnocNo:not([disabled])")
                
                # Select Surnoc
                page.locator("#ctl00_MainContent_ddlOSurnocNo").select_option("*")
                time.sleep(2)  # Wait for server response
                
                # Wait for Hissa dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOHissaNo:not([disabled])")
                
                # Select Hissa
                page.locator("#ctl00_MainContent_ddlOHissaNo").select_option("53")
                time.sleep(2)  # Wait for server response

                # Get all available periods
                period_dropdown = page.locator("#ctl00_MainContent_ddlOPeriod")
                periods = []
                
                # Wait for period dropdown to be enabled
                page.wait_for_selector("#ctl00_MainContent_ddlOPeriod:not([disabled])")
                
                # Get all period options
                period_options = period_dropdown.evaluate("""select => {
                    return Array.from(select.options).map(option => ({
                        value: option.value,
                        text: option.text
                    })).filter(option => option.value !== '0');
                }""")

                documents = []
                
                # Process each period
                for period_option in period_options:
                    period = period_option['value']
                    period_text = period_option['text']
                    target_year = self._extract_year_from_period(period_text)
                    
                    if not target_year:
                        print(f"Could not extract year from period: {period_text}")
                        continue

                    # Skip if year is not in our target range
                    if not self._is_year_in_range(target_year):
                        print(f"Skipping period outside target range: {period_text} ({target_year})")
                        continue
                        
                    try:
                        # Select period
                        page.locator("#ctl00_MainContent_ddlOPeriod").select_option(period)
                        time.sleep(2)
                        
                        # Wait for year dropdown to be enabled
                        page.wait_for_selector("#ctl00_MainContent_ddlOYear:not([disabled])")
                        
                        # Get available years for this period
                        year_dropdown = page.locator("#ctl00_MainContent_ddlOYear")
                        year_options = year_dropdown.evaluate("""select => {
                            return Array.from(select.options).map(option => ({
                                value: option.value,
                                text: option.text
                            })).filter(option => option.value !== '0');
                        }""")
                        
                        # Find the matching year option
                        matching_year = next((year for year in year_options if year['text'] == target_year), None)
                        
                        if not matching_year:
                            print(f"Could not find matching year {target_year} for period {period_text}")
                            continue
                            
                        try:
                            # Select year
                            page.locator("#ctl00_MainContent_ddlOYear").select_option(matching_year['value'])
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
                            
                            # Remove the API upload logic and save screenshots locally
                            screenshot_folder = os.path.join(os.path.dirname(__file__), 'screenshots')
                            os.makedirs(screenshot_folder, exist_ok=True)

                            # Save the screenshot locally
                            screenshot_path = os.path.join(screenshot_folder, f"RTC_{target_year}.png")
                            page1.screenshot(path=screenshot_path)
                            print(f"Screenshot saved locally at: {screenshot_path}")

                            documents.append({
                                'period': period,
                                'period_text': period_text,
                                'year': matching_year['value'],
                                'year_text': matching_year['text'],
                                'screenshot_path': screenshot_path
                            })
                            print(f"Successfully captured screenshot for {period_text} ({target_year})")
                            
                            # Close popup
                            page1.close()
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"Error processing year {matching_year['text']} for period {period_text}: {str(e)}")
                            continue
                            
                    except Exception as e:
                        print(f"Error processing period {period_text}: {str(e)}")
                        continue

                # Create a folder to save screenshots if it doesn't exist
                screenshot_folder = os.path.join(os.path.dirname(__file__), 'screenshots')
                os.makedirs(screenshot_folder, exist_ok=True)

                # Take a screenshot of the receipt when it appears
                receipt_selector = "#ReceiptElement"  # Replace with the actual selector for the receipt
                try:
                    page.wait_for_selector(receipt_selector, timeout=60000)  # Wait for the receipt to appear
                    receipt_screenshot_path = os.path.join(screenshot_folder, 'receipt_screenshot.png')
                    page.locator(receipt_selector).screenshot(path=receipt_screenshot_path)
                    print(f"Receipt screenshot saved at: {receipt_screenshot_path}")
                except Exception as e:
                    print(f"Error taking receipt screenshot: {str(e)}")
                
                return documents
                
            except Exception as e:
                print(f"Error during scraping: {str(e)}")
                return None
                
            finally:
                context.close()
                browser.close()

# Example usage:
if __name__ == "__main__":
    property_data = {
        'survey_number': '22',
        'surnoc': '*',
        'hissa': '1',
        'village': 'Devanahalli',
        'hobli': 'Kasaba',
        'taluk': 'Devenahalli',
        'district': 'Bangalore Rural'
    }
    
    scraper = RTCScraper()
    documents = scraper.scrape_documents(property_data)
    print("Documents:", documents)