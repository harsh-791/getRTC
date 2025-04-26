from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import sys
import os
import uuid
import traceback
from image_processor import ImageProcessor
from scraper import RTCScraper
from db_handler import DBHandler
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import RTCData, RTCDocument
from django.conf import settings
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create your views here.

class ProcessImageView(APIView):
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        image_file = request.FILES['image']
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join('media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create full path
        full_path = os.path.join(temp_dir, filename)
        
        try:
            # Save the file directly to the full path
            with open(full_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Process the image
            processor = ImageProcessor()
            result = processor.extract_info_from_image(full_path)
            
            if result:
                try:
                    # Initialize database handler
                    db_handler = DBHandler(
                        dbname="rtc_documents",
                        user="rtc_user",
                        password="rtc_password",
                        host="localhost",
                        port="5432"
                    )
                    
                    # Initialize scraper with db_handler
                    scraper = RTCScraper(db_handler)
                    
                    # Convert the result to the format expected by the scraper
                    property_data = {
                        'survey_number': result['Survey Number'],
                        'surnoc': result['Surnoc'],
                        'hissa': result['Hissa'],
                        'village': result['Village'],
                        'hobli': result['Hobli'],
                        'taluk': result['Taluk'],
                        'district': result['District']
                    }
                    
                    # Scrape documents
                    documents = scraper.scrape_documents(property_data)
                    
                    # Add scraping results to the response
                    result['scraping_status'] = 'success' if documents else 'failed'
                    result['documents_count'] = len(documents) if documents else 0
                    
                    return Response(result)
                except Exception as e:
                    print(f"Error during scraping: {str(e)}")
                    print(traceback.format_exc())
                    # Return the extracted info even if scraping fails
                    result['scraping_status'] = 'failed'
                    result['documents_count'] = 0
                    return Response(result)
            else:
                return Response({'error': 'Failed to process image'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception as e:
                print(f"Error cleaning up temporary file: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def process_image(request):
    try:
        if not request.FILES.get('image'):
            return JsonResponse({'error': 'No image provided'}, status=400)

        # Save the uploaded image
        uploaded_file = request.FILES['image']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        try:
            # Process the image
            processor = ImageProcessor()
            extracted_info = processor.extract_info_from_image(file_path)
            
            if not extracted_info:
                return JsonResponse({'error': 'Failed to extract information from image'}, status=400)

            # Format the extracted information
            property_data = {
                'survey_number': str(extracted_info.get('Survey Number', '')),
                'surnoc': str(extracted_info.get('Surnoc', '')),
                'hissa': str(extracted_info.get('Hissa', '')),
                'village': str(extracted_info.get('Village', '')),
                'hobli': str(extracted_info.get('Hobli', '')),
                'taluk': str(extracted_info.get('Taluk', '')),
                'district': str(extracted_info.get('District', ''))
            }

            # Run the scraper in an event loop
            scraper = RTCScraper()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scraping_result = loop.run_until_complete(scraper.scrape_documents(property_data))
            loop.close()

            # Find the latest RTCData record for this property
            rtc_data = RTCData.objects.filter(
                survey_number=property_data['survey_number'],
                surnoc=property_data['surnoc'],
                hissa=property_data['hissa'],
                village=property_data['village'],
                hobli=property_data['hobli'],
                taluk=property_data['taluk'],
                district=property_data['district'],
            ).order_by('-created_at').first()

            screenshots = []
            if rtc_data:
                for doc in rtc_data.documents.all():
                    if doc.screenshot_path:
                        screenshots.append({
                            'name': os.path.basename(doc.screenshot_path),
                            'url': f'/media/{doc.screenshot_path}'
                        })

            return JsonResponse({
                'success': True,
                'message': 'Image processed and documents scraped successfully',
                'extracted_info': extracted_info,
                'scraping_result': scraping_result,
                'screenshots': screenshots,
                'record_id': rtc_data.id if rtc_data else None
            })

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'error': f'Error processing image: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=500)

        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)

@require_http_methods(["GET"])
def get_screenshots(request, record_id):
    try:
        rtc_data = RTCData.objects.get(id=record_id)
        documents = rtc_data.documents.all()
        screenshots = []
        for doc in documents:
            if doc.screenshot_path:
                screenshots.append({
                    'name': os.path.basename(doc.screenshot_path),
                    'url': f'/media/{doc.screenshot_path}' if not doc.screenshot_path.startswith('/media/') else doc.screenshot_path
                })
        return JsonResponse({
            'success': True,
            'screenshots': screenshots
        })
    except RTCData.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting screenshots: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
