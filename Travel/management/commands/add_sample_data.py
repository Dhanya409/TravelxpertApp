from django.core.management.base import BaseCommand
from Travel.models import TourPackage, Flight, Itinerary, InclusionsExclusions
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Add sample data to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Sample Tour Packages
        packages = [
            {
                'name': "Goa Beach Paradise",
                'description': "Experience the sun, sand, and vibrant culture of Goa. Enjoy pristine beaches, water sports, delicious seafood, and vibrant nightlife.",
                'price': 25000,
                'available_slots': 20,
                'duration': 5,
                'start_date': timezone.now() + timedelta(days=15),
                'end_date': timezone.now() + timedelta(days=20),
                'location': "Goa",
                'highlights': "Beautiful beaches, Water sports, Nightlife, Local cuisine"
            },
            {
                'name': "Kerala Backwaters",
                'description': "Explore the serene backwaters and lush landscapes of Kerala. Stay in luxury houseboats, experience Ayurvedic treatments, and visit tea plantations.",
                'price': 35000,
                'available_slots': 15,
                'duration': 6,
                'start_date': timezone.now() + timedelta(days=20),
                'end_date': timezone.now() + timedelta(days=26),
                'location': "Kerala",
                'highlights': "Houseboat stay, Ayurveda spa, Tea plantations, Cultural shows"
            },
            {
                'name': "Rajasthan Heritage Tour",
                'description': "Discover the royal heritage and majestic forts of Rajasthan. Experience desert safaris, traditional music, and authentic Rajasthani cuisine.",
                'price': 45000,
                'available_slots': 18,
                'duration': 7,
                'start_date': timezone.now() + timedelta(days=32),
                'end_date': timezone.now() + timedelta(days=39),
                'location': "Rajasthan",
                'highlights': "Palace visits, Desert safari, Folk music, Traditional cuisine"
            },
            {
                'name': "Manali Adventure",
                'description': "Experience thrilling adventures in the snow-capped mountains of Manali. Perfect for adventure enthusiasts and nature lovers.",
                'price': 30000,
                'available_slots': 25,
                'duration': 5,
                'start_date': timezone.now() + timedelta(days=41),
                'end_date': timezone.now() + timedelta(days=46),
                'location': "Manali",
                'highlights': "Skiing, Paragliding, River rafting, Mountain trekking"
            }
        ]

        for package_data in packages:
            # Create tour package
            package = TourPackage.objects.create(
                name=package_data['name'],
                description=package_data['description'],
                price=package_data['price'],
                available_slots=package_data['available_slots'],
                duration=package_data['duration'],
                start_date=package_data['start_date'],
                end_date=package_data['end_date'],
                location=package_data['location'],
                highlights=package_data['highlights']
            )
            
            self.stdout.write(f'Created package: {package.name}')

            # Create inclusions/exclusions for each package
            InclusionsExclusions.objects.create(
                tour_package=package,
                inclusions="""
                - Luxury hotel accommodation (4/5 star)
                - Daily breakfast and dinner
                - Airport/Railway station transfers
                - Local sightseeing with expert guide
                - All entrance fees to monuments
                - Welcome drink on arrival
                - All applicable taxes
                - Travel insurance
                """,
                exclusions="""
                - Airfare/Train fare
                - Personal expenses and tips
                - Additional activities not in itinerary
                - Lunch and beverages
                - Camera fees at monuments
                - Any item not mentioned in inclusions
                """
            )

            # Create sample flights for each package
            flights = [
                {
                    'airline': "Air India",
                    'flight_number': f"AI{package.id}01",
                    'departure_city': "Mumbai",
                    'price': 8000,
                    'available_seats': 50
                },
                {
                    'airline': "IndiGo",
                    'flight_number': f"6E{package.id}02",
                    'departure_city': "Delhi",
                    'price': 7500,
                    'available_seats': 45
                },
                {
                    'airline': "SpiceJet",
                    'flight_number': f"SG{package.id}03",
                    'departure_city': "Bangalore",
                    'price': 8500,
                    'available_seats': 40
                }
            ]

            for flight_data in flights:
                Flight.objects.create(
                    airline=flight_data['airline'],
                    flight_number=flight_data['flight_number'],
                    departure_city=flight_data['departure_city'],
                    arrival_city=package.location,
                    departure_date=package.start_date,
                    arrival_date=package.start_date,
                    departure_time="10:00",
                    arrival_time="12:00",
                    price=flight_data['price'],
                    available_seats=flight_data['available_seats']
                )
                self.stdout.write(f'Created flight: {flight_data["flight_number"]}')

            # Create sample itinerary
            itinerary_days = [
                {
                    'day_number': 1,
                    'title': f"Welcome to {package.location}",
                    'description': f"""
                    Arrive at {package.location} airport/railway station
                    Transfer to hotel and check-in
                    Welcome drink and orientation
                    Evening free for leisure
                    Dinner at hotel
                    """
                },
                {
                    'day_number': 2,
                    'title': "Local Sightseeing",
                    'description': f"""
                    Breakfast at hotel
                    Full day local sightseeing
                    Visit to major attractions
                    Evening cultural activities
                    Dinner at hotel
                    """
                },
                {
                    'day_number': 3,
                    'title': "Adventure Activities",
                    'description': f"""
                    Early breakfast
                    Full day adventure activities
                    Packed lunch
                    Evening relaxation time
                    Special dinner with local delicacies
                    """
                }
            ]

            for day in itinerary_days:
                Itinerary.objects.create(
                    tour_package=package,
                    day_number=day['day_number'],
                    title=day['title'],
                    description=day['description']
                )
                self.stdout.write(f'Created itinerary for day {day["day_number"]}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))
