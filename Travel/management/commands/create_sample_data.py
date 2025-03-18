from django.core.management.base import BaseCommand
from Travel.models import TourPackage, Flight, Passenger, FlightBooking, InclusionsExclusions, Itinerary
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creates sample data for the travel application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create sample tour packages
        packages = [
            {
                'name': 'Goa Beach Paradise',
                'description': 'Experience the perfect beach holiday in Goa with premium resorts and activities',
                'price': 25000,
                'available_slots': 20,
                'duration': '5 Days, 4 Nights',
                'start_date': datetime.now().date() + timedelta(days=15),
                'end_date': datetime.now().date() + timedelta(days=19),
                'location': 'Goa',
                'highlights': 'Beautiful Beaches\nWater Sports\nNightlife\nPortuguese Architecture'
            },
            {
                'name': 'Kerala Backwaters Tour',
                'description': 'Explore the serene backwaters of Kerala in traditional houseboats',
                'price': 35000,
                'available_slots': 15,
                'duration': '6 Days, 5 Nights',
                'start_date': datetime.now().date() + timedelta(days=20),
                'end_date': datetime.now().date() + timedelta(days=25),
                'location': 'Kerala',
                'highlights': 'Houseboat Stay\nAyurvedic Spa\nTea Gardens\nWildlife Sanctuaries'
            },
            {
                'name': 'Manali Adventure',
                'description': 'Experience thrilling adventures in the mountains of Manali',
                'price': 28000,
                'available_slots': 25,
                'duration': '4 Days, 3 Nights',
                'start_date': datetime.now().date() + timedelta(days=10),
                'end_date': datetime.now().date() + timedelta(days=13),
                'location': 'Manali',
                'highlights': 'Skiing\nParagliding\nRiver Rafting\nCamping'
            }
        ]

        created_packages = []
        for package_data in packages:
            package = TourPackage.objects.create(**package_data)
            created_packages.append(package)
            self.stdout.write(f'Created package: {package.name}')

            # Create inclusions/exclusions for each package
            InclusionsExclusions.objects.create(
                tour_package=package,
                inclusions="""
                - Accommodation in 4/5 star hotels
                - All meals (Breakfast, Lunch, Dinner)
                - All transfers and sightseeing
                - Professional guide
                - All activities mentioned
                - All applicable taxes
                """,
                exclusions="""
                - Airfare
                - Personal expenses
                - Additional activities
                - Travel insurance
                - Tips and gratuities
                """
            )

            # Create itinerary for each package
            for day in range(1, int(package_data['duration'].split()[0])):
                Itinerary.objects.create(
                    tour_package=package,
                    day_number=day,
                    title=f'Day {day} - Adventure',
                    description=f'Exciting activities and sightseeing planned for day {day}'
                )

        # Create sample flights
        flights = [
            {
                'flight_number': 'AI101',
                'airline': 'Air India',
                'departure_city': 'Mumbai',
                'arrival_city': 'Goa',
                'departure_date': datetime.now().date() + timedelta(days=15),
                'departure_time': datetime.now().replace(hour=10, minute=0).time(),
                'arrival_date': datetime.now().date() + timedelta(days=15),
                'arrival_time': datetime.now().replace(hour=11, minute=30).time(),
                'price': 5000,
                'available_seats': 50
            },
            {
                'flight_number': 'AI102',
                'airline': 'Air India',
                'departure_city': 'Mumbai',
                'arrival_city': 'Kerala',
                'departure_date': datetime.now().date() + timedelta(days=20),
                'departure_time': datetime.now().replace(hour=14, minute=0).time(),
                'arrival_date': datetime.now().date() + timedelta(days=20),
                'arrival_time': datetime.now().replace(hour=16, minute=30).time(),
                'price': 7000,
                'available_seats': 45
            },
            {
                'flight_number': 'AI103',
                'airline': 'Air India',
                'departure_city': 'Mumbai',
                'arrival_city': 'Manali',
                'departure_date': datetime.now().date() + timedelta(days=10),
                'departure_time': datetime.now().replace(hour=8, minute=0).time(),
                'arrival_date': datetime.now().date() + timedelta(days=10),
                'arrival_time': datetime.now().replace(hour=10, minute=30).time(),
                'price': 6000,
                'available_seats': 55
            }
        ]

        for flight_data in flights:
            flight = Flight.objects.create(**flight_data)
            self.stdout.write(f'Created flight: {flight.flight_number}')

        # Create sample users and passengers
        users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        ]

        for user_data in users:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='testpass123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Create passenger profile for each user
            passenger = Passenger.objects.create(
                full_name=f"{user_data['first_name']} {user_data['last_name']}",
                email=user_data['email'],
                phone='9876543210',
                age=30
            )
            self.stdout.write(f'Created passenger: {passenger.full_name}')

            # Create sample bookings
            flight = Flight.objects.first()
            package = TourPackage.objects.first()
            if flight and package:
                booking = FlightBooking.objects.create(
                    passenger=passenger,
                    flight=flight,
                    tour_package=package,
                    seat_class='economy',
                    booking_status='confirmed',
                    total_amount=flight.price + package.price
                )
                self.stdout.write(f'Created booking for: {passenger.full_name}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))
