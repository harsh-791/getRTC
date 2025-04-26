from image_processor import ImageProcessor
import json
import os

def test_image_processor():
    # Initialize the image processor
    processor = ImageProcessor()
    
    # Test with multiple images
    test_images = [
        "RTC.png",
        "RTC_2015-08-19_16_54_00_To_2022-04-11_13_53_00__2017-2018___2017-2018.png"
    ]
    
    for image_name in test_images:
        # Use the provided RTC image path from screenshots folder
        image_path = os.path.join("screenshots", image_name)
        
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"\nError: Image not found at {image_path}")
            continue
        
        # Process the image
        print(f"\nProcessing image: {image_path}")
        print("-" * 50)
        
        extracted_info = processor.extract_info_from_image(image_path)
        
        if extracted_info:
            print("\nExtracted Information:")
            print("-" * 50)
            fields = [
                "Survey Number",
                "Surnoc",
                "Hissa",
                "Village",
                "Hobli",
                "Taluk",
                "District"
            ]
            
            for field in fields:
                value = extracted_info.get(field, "NA")
                print(f"{field:15}: {value}")
            
            print("\nJSON Output:")
            print("-" * 50)
            print(json.dumps(extracted_info, indent=2))
            
            print("\nFormatted Output:")
            print("-" * 50)
            print(processor.format_for_scraper(extracted_info))
        else:
            print("Failed to extract information from the image.")

if __name__ == "__main__":
    test_image_processor() 