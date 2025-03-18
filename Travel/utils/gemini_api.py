import google.cloud.vision as vision
import google.generativeai as genai
import PIL.Image
import json
import os
from django.conf import settings
from typing import List, Dict, Any, Optional
from functools import lru_cache

# Get API key from environment variable or settings
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize model once
model = genai.GenerativeModel('gemini-pro')

def initialize_vision():
    try:
        # Initialize the client
        client = vision.ImageAnnotatorClient.from_service_account_json('landmark-detection-key.json')
        return client
    except Exception as e:
        print(f"Error initializing Google Cloud Vision API: {str(e)}")
        return None

def process_image(image_path):
    try:
        # Open and validate image
        img = PIL.Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (max 4MB for Google Cloud Vision API)
        max_size = (1024, 1024)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, PIL.Image.Resampling.LANCZOS)
            
        # Save processed image
        processed_path = image_path.replace('.', '_processed.')
        img.save(processed_path, 'JPEG', quality=85)
        return processed_path
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def detect_landmark(image_path):
    """Detects landmarks in an image using Google Cloud Vision API."""
    try:
        # Initialize the client
        client = initialize_vision()
        if not client:
            raise Exception("Failed to initialize Google Cloud Vision API")

        # Process image
        processed_path = process_image(image_path)
        if not processed_path:
            raise Exception("Failed to process image")

        # Read the image file
        with open(processed_path, 'rb') as image_file:
            content = image_file.read()

        # Create an image object
        image = vision.Image(content=content)

        # Perform landmark detection
        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations

        if not landmarks:
            return {
                'landmark_name': 'Unknown Landmark',
                'description': 'No landmark detected in the image.',
                'history': 'No historical information available.',
                'location': 'Location unknown',
                'confidence_score': 0.0
            }

        # Get the most likely landmark (first result)
        landmark = landmarks[0]
        
        # Extract location information
        location = 'Location unknown'
        if landmark.locations:
            lat_lng = landmark.locations[0].lat_lng
            location = f"Latitude: {lat_lng.latitude}, Longitude: {lat_lng.longitude}"

        # Clean up processed image
        try:
            os.remove(processed_path)
        except:
            pass

        return {
            'landmark_name': landmark.description,
            'description': f"This appears to be {landmark.description}",
            'history': f"This is a recognized landmark with a confidence score of {landmark.score:.2%}",
            'location': location,
            'confidence_score': landmark.score
        }

    except Exception as e:
        print(f"Error in landmark detection: {str(e)}")
        return None







def generate_packing_list(
    trip_types: List[str],
    weather: str,
    traveling_with_kids: bool = False,
    special_requirements: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a personalized packing list instantly using pre-defined templates.
    """
    try:
        # Validate inputs
        if not trip_types:
            raise ValueError("At least one trip type must be specified")
        if weather not in ['hot', 'cold', 'moderate', 'rainy']:
            raise ValueError(f"Invalid weather condition: {weather}")

        # Pre-defined packing lists
        packing_list = {
            'source': 'optimized',
            'categories': {
                'essential_documents': [
                    "Passport/ID",
                    "Travel insurance",
                    "Booking confirmations",
                    "Emergency contacts",
                    "Local currency"
                ],
                'clothing': [],  # Will be filled based on weather
                'toiletries': [
                    "Toothbrush & toothpaste",
                    "Shampoo & conditioner",
                    "Soap/body wash",
                    "Deodorant",
                    "Medications",
                    "First aid kit",
                    "Sunscreen",
                    "Hand sanitizer"
                ],
                'electronics': [
                    "Phone & charger",
                    "Power bank",
                    "Universal adapter",
                    "Camera (optional)",
                    "Headphones"
                ],
                'trip_specific_items': []  # Will be filled based on trip types
            }
        }

        # Add weather-specific clothing
        weather_clothing = {
            'hot': [
                "Light, breathable shirts",
                "Shorts/light pants",
                "Sunhat",
                "Sunglasses",
                "Light jacket for AC",
                "Comfortable walking shoes",
                "Sandals"
            ],
            'cold': [
                "Warm sweaters",
                "Thermal underlayers",
                "Winter coat",
                "Gloves and scarf",
                "Warm socks",
                "Winter boots",
                "Warm hat"
            ],
            'moderate': [
                "Mix of light and warm clothes",
                "Long sleeve shirts",
                "Light jacket",
                "Comfortable pants",
                "Walking shoes",
                "Light sweater"
            ],
            'rainy': [
                "Rain jacket/umbrella",
                "Waterproof shoes",
                "Quick-dry clothing",
                "Extra socks",
                "Waterproof bag cover"
            ]
        }
        packing_list['categories']['clothing'] = weather_clothing.get(weather, weather_clothing['moderate'])

        # Add trip-specific items
        trip_specific_items = {
            'beach': [
                "Swimwear",
                "Beach towel",
                "Beach bag",
                "Flip flops",
                "Beach umbrella/tent",
                "Water bottle"
            ],
            'adventure': [
                "Hiking boots",
                "Backpack",
                "Water bottle",
                "Compass/maps",
                "First aid kit",
                "Flashlight"
            ],
            'business': [
                "Business suits",
                "Formal shoes",
                "Business cards",
                "Laptop & charger",
                "Notebook/pen",
                "Professional accessories"
            ],
            'cultural': [
                "Modest clothing",
                "Head covering (if needed)",
                "Camera",
                "Guidebook",
                "Language translator",
                "Comfortable walking shoes"
            ],
            'religious': [
                "Modest clothing",
                "Head covering",
                "Religious items",
                "Appropriate footwear",
                "Prayer materials"
            ],
            'shopping': [
                "Comfortable shoes",
                "Extra bag for purchases",
                "Shopping list",
                "Calculator",
                "Secure wallet"
            ]
        }

        for trip_type in trip_types:
            if trip_type in trip_specific_items:
                packing_list['categories']['trip_specific_items'].extend(trip_specific_items[trip_type])

        # Add kids items if needed
        if traveling_with_kids:
            packing_list['categories']['kids_essentials'] = [
                "Children's clothes",
                "Favorite toys/games",
                "Snacks",
                "Baby wipes",
                "Diapers (if needed)",
                "Children's medications",
                "Entertainment items"
            ]

        # Add any special requirements as notes
        if special_requirements:
            packing_list['categories']['special_notes'] = [special_requirements]

        return packing_list

    except Exception as e:
        print(f"Error generating packing list: {str(e)}")
        # Return a simplified default list
        return {
            'source': 'default',
            'categories': {
                'essential_documents': ["Passport/ID", "Travel documents"],
                'clothing': ["Weather-appropriate clothing", "Comfortable shoes"],
                'toiletries': ["Basic toiletries", "Medications"],
                'electronics': ["Phone & charger"],
                'health_and_safety': ["First aid kit", "Emergency contacts"]
            }
        }
