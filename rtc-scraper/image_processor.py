import os
from openai import OpenAI
from dotenv import load_dotenv
import base64
from typing import Dict, Optional
import json

# Load environment variables from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class ImageProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_info_from_image(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Extract information from image using OpenAI's vision API.
        Returns a dictionary with the required fields or None if extraction fails.
        """
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Call OpenAI's vision API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at reading Kannada RTC (Village Account Form) documents. 
            Your task is to extract specific fields from the document.

            FIELD LOCATIONS:
            1. Survey Number (ಸರ್ವೆ ನಂಬರ್):
               - Look for numbers in the top-left section
               - Usually 1-3 digits
               - Common label: "ಸರ್ವೆ ಸಂಖ್ಯೆ"

            2. Surnoc:
               - Always return "*"

            3. Hissa (ಹಿಸ್ಸಾ):
               - Look for numbers near Survey Number
               - Usually a single digit
               - Common label: "ಹಿಸ್ಸಾ"

            4. Administrative Divisions:
               Look in the header section for:
               - Village (ಗ್ರಾಮ): After ಗ್ರಾಮ: or ಗ್ರಾಮದ ಹೆಸರು
               - Hobli (ಹೋಬಳಿ): After ಹೋಬಳಿ:
               - Taluk (ತಾಲ್ಲೂಕು): After ತಾಲ್ಲೂಕು:
               - District (ಜಿಲ್ಲೆ): After ಜಿಲ್ಲೆ:

            EXTRACTION RULES:
            1. For Survey Number and Hissa:
               - Extract only numbers
               - Remove any extra characters
               - If unclear, make your best guess

            2. For Village, Hobli, Taluk, District:
               - Translate Kannada to English
               - Use proper capitalization
               - Common translations:
                 * ದೇವನಹಳ್ಳಿ → Devanahalli
                 * ಕಸಬಾ → Kasaba
                 * ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ → Bangalore Rural

            Return in this JSON format:
            {
                "Survey Number": "number",
                "Surnoc": "*",
                "Hissa": "number",
                "Village": "name",
                "Hobli": "name",
                "Taluk": "name",
                "District": "name"
            }"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Please analyze this RTC document and extract the following information:
            1. Survey Number (look for numbers in top-left)
            2. Hissa (look for numbers near Survey Number)
            3. Village (translate from Kannada)
            4. Hobli (translate from Kannada)
            5. Taluk (translate from Kannada)
            6. District (translate from Kannada)

            Return the information in JSON format."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.3,  # Increased temperature for more confident responses
                top_p=0.9  # Added top_p for better response diversity
            )
            
            # Extract the JSON response
            extracted_text = response.choices[0].message.content
            
            # Try to extract just the JSON part from the response
            try:
                # Find the JSON block in the response
                json_start = extracted_text.find('{')
                json_end = extracted_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = extracted_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("No JSON found in response", extracted_text, 0)
                
                # Ensure all required fields are present with NA as default
                required_fields = {
                    "Survey Number": "NA",
                    "Surnoc": "*",
                    "Hissa": "NA",
                    "Village": "NA",
                    "Hobli": "NA",
                    "Taluk": "NA",
                    "District": "NA"
                }
                
                # Update the result with any missing fields
                for field, default_value in required_fields.items():
                    if field not in result:
                        result[field] = default_value
                    elif not result[field] or result[field].lower() in ['not visible', 'not clear', 'unclear', 'not found', 'none']:
                        result[field] = default_value
                
                # Post-process the results
                result = self.post_process_results(result)
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return None
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    
    def post_process_results(self, result: Dict[str, str]) -> Dict[str, str]:
        """
        Post-process the extracted results to ensure consistency and accuracy.
        """
        # Clean up Survey Number
        if result["Survey Number"] != "NA":
            # Remove any extra spaces or characters, keep only numbers
            cleaned = ''.join(filter(str.isdigit, result["Survey Number"]))
            result["Survey Number"] = cleaned if cleaned else "NA"
        
        # Always set Surnoc to "*"
        result["Surnoc"] = "*"
        
        # Clean up Hissa
        if result["Hissa"] != "NA":
            # Remove any extra spaces or characters, keep only numbers
            cleaned = ''.join(filter(str.isdigit, result["Hissa"]))
            result["Hissa"] = cleaned if cleaned else "NA"
        
        # Clean up place names
        for field in ["Village", "Hobli", "Taluk", "District"]:
            if result[field] != "NA":
                # Remove extra spaces and standardize capitalization
                cleaned = result[field].strip().title()
                # If after cleaning it's empty or contains unclear indicators, set to NA
                if not cleaned or any(x in cleaned.lower() for x in ['not visible', 'not clear', 'unclear', 'not found', 'none', 'null']):
                    result[field] = "NA"
                else:
                    result[field] = cleaned
        
        return result
    
    def format_for_scraper(self, extracted_info: Dict[str, str]) -> str:
        """
        Format the extracted information into a string that can be passed to the scraper.
        """
        return f"""
        Survey Number: {extracted_info['Survey Number']}
        Surnoc: {extracted_info['Surnoc']}
        Hissa: {extracted_info['Hissa']}
        Village: {extracted_info['Village']}
        Hobli: {extracted_info['Hobli']}
        Taluk: {extracted_info['Taluk']}
        District: {extracted_info['District']}
        """

# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    # Replace with actual image path
    image_path = "path_to_your_image.jpg"
    extracted_info = processor.extract_info_from_image(image_path)
    if extracted_info:
        print("Extracted Information (JSON):")
        print(json.dumps(extracted_info, indent=2))
        print("\nFormatted for Scraper:")
        print(processor.format_for_scraper(extracted_info))