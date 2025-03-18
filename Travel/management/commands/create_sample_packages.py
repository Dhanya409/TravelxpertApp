from django.core.management.base import BaseCommand
from Travel.models import TourPackage
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Creates sample tour packages for each category'

    def handle(self, *args, **kwargs):
        # First, delete all existing packages
        TourPackage.objects.all().delete()
        
        # Sample packages data
        packages_data = {
            # Destination-Based Packages
            'domestic': [
                {
                    'name': 'Kerala Backwaters Explorer',
                    'description': 'Experience the serene backwaters of Kerala, visit spice plantations, and enjoy traditional Ayurvedic treatments.',
                    'price': 25000,
                    'duration': '5 days, 4 nights',
                    'location': 'Kerala, India',
                },
                {
                    'name': 'Rajasthan Royal Heritage',
                    'description': 'Explore majestic palaces, ancient forts, and experience the royal culture of Rajasthan.',
                    'price': 35000,
                    'duration': '7 days, 6 nights',
                    'location': 'Rajasthan, India',
                },
                {
                    'name': 'Himalayan Adventure',
                    'description': 'Trek through beautiful Himalayan trails, visit monasteries, and experience local culture.',
                    'price': 28000,
                    'duration': '6 days, 5 nights',
                    'location': 'Himachal Pradesh, India',
                },
            ],
            'international': [
                {
                    'name': 'Bali Paradise',
                    'description': 'Discover beautiful beaches, ancient temples, and vibrant culture of Bali.',
                    'price': 75000,
                    'duration': '6 days, 5 nights',
                    'location': 'Bali, Indonesia',
                },
                {
                    'name': 'Dubai Extravaganza',
                    'description': 'Experience luxury shopping, desert safari, and modern architectural marvels.',
                    'price': 95000,
                    'duration': '5 days, 4 nights',
                    'location': 'Dubai, UAE',
                },
                {
                    'name': 'Thailand Discovery',
                    'description': 'Explore beautiful islands, ancient temples, and enjoy Thai cuisine.',
                    'price': 65000,
                    'duration': '7 days, 6 nights',
                    'location': 'Thailand',
                },
            ],
            # Theme-Based Packages
            'adventure': [
                {
                    'name': 'Rishikesh River Rafting',
                    'description': 'Experience thrilling white water rafting, camping, and adventure sports.',
                    'price': 22000,
                    'duration': '4 days, 3 nights',
                    'location': 'Rishikesh, India',
                },
                {
                    'name': 'Andaman Scuba Adventure',
                    'description': 'Discover underwater marine life through scuba diving and snorkeling.',
                    'price': 45000,
                    'duration': '6 days, 5 nights',
                    'location': 'Andaman Islands',
                },
                {
                    'name': 'Ladakh Bike Expedition',
                    'description': 'Motorcycle journey through the highest motorable roads and stunning landscapes.',
                    'price': 35000,
                    'duration': '8 days, 7 nights',
                    'location': 'Ladakh, India',
                },
            ],
            'romantic': [
                {
                    'name': 'Maldives Honeymoon',
                    'description': 'Stay in overwater villas, enjoy couple spa treatments, and romantic dinners.',
                    'price': 120000,
                    'duration': '5 days, 4 nights',
                    'location': 'Maldives',
                },
                {
                    'name': 'Paris Romance',
                    'description': 'Experience the city of love with Eiffel Tower views and Seine River cruise.',
                    'price': 150000,
                    'duration': '7 days, 6 nights',
                    'location': 'Paris, France',
                },
                {
                    'name': 'Udaipur Lake Palace',
                    'description': 'Stay in luxury palace hotels, enjoy boat rides, and cultural performances.',
                    'price': 85000,
                    'duration': '4 days, 3 nights',
                    'location': 'Udaipur, India',
                },
            ],
            'family': [
                {
                    'name': 'Singapore Family Fun',
                    'description': 'Visit Universal Studios, Singapore Zoo, and enjoy family activities.',
                    'price': 85000,
                    'duration': '6 days, 5 nights',
                    'location': 'Singapore',
                },
                {
                    'name': 'Kerala Family Adventure',
                    'description': 'Explore wildlife sanctuaries, tea plantations, and enjoy family-friendly activities.',
                    'price': 45000,
                    'duration': '5 days, 4 nights',
                    'location': 'Kerala, India',
                },
                {
                    'name': 'Goa Beach Holiday',
                    'description': 'Beach activities, water sports, and family entertainment.',
                    'price': 35000,
                    'duration': '4 days, 3 nights',
                    'location': 'Goa, India',
                },
            ],
            'wellness': [
                {
                    'name': 'Rishikesh Yoga Retreat',
                    'description': 'Daily yoga sessions, meditation, and spiritual guidance.',
                    'price': 30000,
                    'duration': '7 days, 6 nights',
                    'location': 'Rishikesh, India',
                },
                {
                    'name': 'Kerala Ayurveda Package',
                    'description': 'Traditional Ayurvedic treatments, yoga, and healthy cuisine.',
                    'price': 40000,
                    'duration': '8 days, 7 nights',
                    'location': 'Kerala, India',
                },
                {
                    'name': 'Himalayan Meditation Retreat',
                    'description': 'Guided meditation, nature walks, and spiritual workshops.',
                    'price': 35000,
                    'duration': '6 days, 5 nights',
                    'location': 'Dharamshala, India',
                },
            ],
            # Budget-Based Packages
            'budget': [
                {
                    'name': 'Manali Budget Trip',
                    'description': 'Affordable mountain getaway with basic accommodations and activities.',
                    'price': 15000,
                    'duration': '4 days, 3 nights',
                    'location': 'Manali, India',
                },
                {
                    'name': 'Gokarna Beach Break',
                    'description': 'Budget-friendly beach holiday with basic accommodations.',
                    'price': 12000,
                    'duration': '3 days, 2 nights',
                    'location': 'Gokarna, India',
                },
                {
                    'name': 'Varanasi Spiritual Tour',
                    'description': 'Budget spiritual journey with simple accommodations.',
                    'price': 10000,
                    'duration': '3 days, 2 nights',
                    'location': 'Varanasi, India',
                },
            ],
            'mid_range': [
                {
                    'name': 'Golden Triangle Tour',
                    'description': 'Comfortable tour of Delhi, Agra, and Jaipur with good hotels.',
                    'price': 45000,
                    'duration': '6 days, 5 nights',
                    'location': 'Delhi-Agra-Jaipur',
                },
                {
                    'name': 'Kashmir Valley Tour',
                    'description': 'Mid-range accommodations with scenic valley views and activities.',
                    'price': 38000,
                    'duration': '5 days, 4 nights',
                    'location': 'Kashmir, India',
                },
                {
                    'name': 'Bhutan Experience',
                    'description': 'Comfortable tour of the Land of Thunder Dragon.',
                    'price': 55000,
                    'duration': '7 days, 6 nights',
                    'location': 'Bhutan',
                },
            ],
            'luxury': [
                {
                    'name': 'Royal Rajasthan Luxury',
                    'description': 'Stay in palace hotels, luxury train journey, and premium experiences.',
                    'price': 250000,
                    'duration': '8 days, 7 nights',
                    'location': 'Rajasthan, India',
                },
                {
                    'name': 'Kerala Luxury Houseboat',
                    'description': 'Premium houseboat experience with personal chef and luxury amenities.',
                    'price': 180000,
                    'duration': '5 days, 4 nights',
                    'location': 'Kerala, India',
                },
                {
                    'name': 'Himalayan Luxury Escape',
                    'description': 'Luxury resort stay with premium amenities and exclusive experiences.',
                    'price': 200000,
                    'duration': '6 days, 5 nights',
                    'location': 'Uttarakhand, India',
                },
            ],
        }

        # Create packages
        start_date = date.today() + timedelta(days=30)
        for category, packages in packages_data.items():
            for idx, package_data in enumerate(packages):
                # Stagger start dates for variety
                package_start = start_date + timedelta(days=(idx * 7))
                duration_days = int(package_data['duration'].split()[0])
                package_end = package_start + timedelta(days=duration_days)

                TourPackage.objects.create(
                    name=package_data['name'],
                    description=package_data['description'],
                    price=package_data['price'],
                    available_slots=20,
                    duration=package_data['duration'],
                    start_date=package_start,
                    end_date=package_end,
                    location=package_data['location'],
                    category=category,
                    highlights=f"Key highlights for {package_data['name']}",
                    is_active=True
                )

        self.stdout.write(self.style.SUCCESS('Successfully created sample packages'))
