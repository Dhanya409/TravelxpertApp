"""
Packing list generator utility that uses Gemini AI to generate personalized packing lists.
"""

from .gemini_api import generate_packing_list

def get_base_items():
    """Get base items that are common for all trip types."""
    return {
        'documents': [
            'Passport',
            'Visa (if required)',
            'Travel insurance documents',
            'Booking confirmations',
            'Emergency contacts',
            'Vaccination records (if required)',
            'Travel itinerary'
        ],
        'toiletries': [
            'Toothbrush & toothpaste',
            'Shampoo & conditioner',
            'Body wash/soap',
            'Deodorant',
            'Sunscreen',
            'Hand sanitizer',
            'First aid kit',
            'Personal medications',
            'Hair care items'
        ],
        'electronics': [
            'Phone & charger',
            'Power bank',
            'Universal power adapter',
            'Camera (optional)',
            'Headphones',
            'E-reader/books'
        ]
    }

TRIP_TYPE_ITEMS = {
    'adventure': {
        'clothing': [
            'Moisture-wicking t-shirts',
            'Hiking pants/shorts',
            'Waterproof jacket',
            'Hiking boots/sturdy shoes',
            'Sports socks',
            'Quick-dry underwear',
            'Sun hat/cap',
            'Swimwear',
            'Light fleece/sweater',
            'Rain gear'
        ],
        'accessories': [
            'Backpack/daypack',
            'Water bottle',
            'Sunglasses',
            'Camping gear (if needed)',
            'Compass/GPS',
            'Flashlight/headlamp',
            'Multi-tool',
            'Insect repellent'
        ],
        'miscellaneous': [
            'Energy bars/snacks',
            'Maps',
            'Emergency whistle',
            'Rope/paracord',
            'Waterproof bags',
            'Basic repair kit'
        ]
    },
    'beach': {
        'clothing': [
            'Swimsuits (2-3)',
            'Beach cover-ups',
            'Light t-shirts/tank tops',
            'Shorts',
            'Sundresses',
            'Light sleepwear',
            'Flip-flops/sandals',
            'Light jacket for evenings',
            'Casual evening wear'
        ],
        'accessories': [
            'Beach bag',
            'Beach towels',
            'Sun hat',
            'Sunglasses',
            'Water shoes',
            'Beach umbrella/tent'
        ],
        'miscellaneous': [
            'Beach games/activities',
            'Reading materials',
            'Waterproof phone case',
            'After-sun lotion',
            'Insect repellent',
            'Dry bags'
        ]
    },
    'business': {
        'clothing': [
            'Business suits (2-3)',
            'Dress shirts/blouses',
            'Business casual pants/skirts',
            'Professional shoes',
            'Dress socks/stockings',
            'Belt',
            'Professional outerwear',
            'Business casual attire',
            'Evening wear'
        ],
        'accessories': [
            'Laptop bag/briefcase',
            'Professional watch',
            'Business cards',
            'Tie/scarf',
            'Professional accessories',
            'Umbrella'
        ],
        'miscellaneous': [
            'Notebook/planner',
            'Business documents',
            'Presentation materials',
            'Portable office supplies',
            'Breath mints',
            'Stain remover'
        ]
    },
    'cultural': {
        'clothing': [
            'Modest clothing options',
            'Long skirts/pants',
            'Shirts with sleeves',
            'Scarves/shawls',
            'Comfortable walking shoes',
            'Dress shoes',
            'Light jacket/cardigan',
            'Traditional wear (if appropriate)',
            'Weather-appropriate layers'
        ],
        'accessories': [
            'Day bag/backpack',
            'Money belt',
            'Scarf/head covering',
            'Comfortable bag',
            'Photography gear',
            'Travel journal'
        ],
        'miscellaneous': [
            'Language guide/translator',
            'Cultural guidebook',
            'Small gifts for hosts',
            'Religious items (if needed)',
            'Local currency',
            'Travel umbrella'
        ]
    },
    'luxury': {
        'clothing': [
            'Designer casual wear',
            'Formal evening wear',
            'Cocktail attire',
            'Designer shoes',
            'Resort wear',
            'High-end accessories',
            'Designer swimwear',
            'Luxury outerwear',
            'Spa attire'
        ],
        'accessories': [
            'Designer sunglasses',
            'Luxury watch',
            'Fine jewelry',
            'Evening bag/clutch',
            'Designer day bag',
            'Silk scarf/tie'
        ],
        'miscellaneous': [
            'High-end toiletries',
            'Luxury skincare products',
            'Evening accessories',
            'Spa accessories',
            'Fine fragrances',
            'Personal concierge contacts'
        ]
    }
}

SPECIAL_NEEDS_ITEMS = {
    'baby': {
        'essentials': [
            'Diapers & wipes',
            'Baby food & formula',
            'Baby bottles & sterilizing equipment',
            'Baby clothes (multiple changes)',
            'Baby blanket',
            'Baby carrier/sling',
            'Stroller/pram',
            'Baby medications',
            'Baby first aid kit',
            'Baby monitor'
        ],
        'comfort': [
            'Favorite toys',
            'Pacifiers',
            'Baby books',
            'Portable crib/travel cot',
            'Baby sleeping bag',
            'White noise machine'
        ],
        'hygiene': [
            'Baby shampoo & wash',
            'Diaper rash cream',
            'Baby lotion',
            'Baby sunscreen',
            'Baby towels',
            'Changing mat'
        ]
    },
    'elderly': {
        'medical': [
            'Prescription medications',
            'Medical documents & insurance cards',
            'List of doctors & emergency contacts',
            'Medical alert bracelet/card',
            'Blood pressure monitor',
            'Glucose monitor (if diabetic)',
            'Pain relief medication'
        ],
        'mobility': [
            'Walking aid/cane',
            'Wheelchair/walker (if needed)',
            'Non-slip shoes',
            'Grip socks',
            'Seat cushion'
        ],
        'comfort': [
            'Reading glasses & case',
            'Hearing aids & batteries',
            'Extra warm clothing',
            'Compression socks',
            'Easy-to-wear clothing'
        ]
    }
}

def generate_personalized_packing_list(package, preferences):
    """
    Generate a personalized packing list based on trip preferences using Gemini AI.
    
    Args:
        package: The travel package
        preferences: PackingPreferences object containing user preferences
    
    Returns:
        dict: Categorized packing list
    """
    # Extract trip types from preferences
    trip_types = preferences.trip_categories
    
    # Get weather preference
    weather = preferences.weather
    
    # Check if traveling with kids
    traveling_with_kids = preferences.traveling_with_kids
    
    # Get any special requirements
    special_requirements = preferences.special_requirements or ''
    
    # Generate packing list using Gemini AI
    packing_list = generate_packing_list(
        trip_types=trip_types,
        weather=weather,
        traveling_with_kids=traveling_with_kids,
        special_requirements=special_requirements
    )
    
    return packing_list
