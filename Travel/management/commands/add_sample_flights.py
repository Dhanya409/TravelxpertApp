from django.core.management.base import BaseCommand
from Travel.models import Flight, TourPackage
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Add sample flights matching tour package dates'

    def handle(self, *args, **kwargs):
        # Get all tour packages
        packages = TourPackage.objects.all()
        
        # Airlines list
        airlines = [
            'IndiGo', 'Air India', 'SpiceJet', 'Vistara', 
            'Go First', 'AirAsia India', 'Air India Express'
        ]
        
        # Base prices for different routes
        base_prices = {
            'Delhi': 5000,
            'Mumbai': 6000,
            'Bangalore': 5500,
            'Chennai': 5800,
            'Kolkata': 6200,
            'Hyderabad': 5300,
            'Goa': 4800,
        }
        
        flights_created = 0
        
        for package in packages:
            # Create 3-5 flights for each package
            num_flights = random.randint(3, 5)
            
            for _ in range(num_flights):
                # Generate flight details
                airline = random.choice(airlines)
                flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
                
                # Set departure time to morning/afternoon on package start date
                departure_hour = random.randint(6, 18)
                departure_time = datetime.combine(package.start_date, datetime.min.time().replace(hour=departure_hour))
                
                # Flight duration between 2-4 hours
                duration_hours = random.uniform(2, 4)
                arrival_time = departure_time + timedelta(hours=duration_hours)
                
                # Base price + random variation
                base_price = base_prices.get(package.location, 5000)
                price_variation = random.uniform(0.8, 1.2)
                price = round(base_price * price_variation, -2)  # Round to nearest 100
                
                # Create the flight
                flight = Flight.objects.create(
                    flight_number=flight_number,
                    airline=airline,
                    departure_city='Mumbai',  # Assuming Mumbai as base city
                    arrival_city=package.location,
                    departure_date=package.start_date,
                    departure_time=departure_time.time(),
                    arrival_date=package.start_date,
                    arrival_time=arrival_time.time(),
                    price=price,
                    available_seats=random.randint(10, 50)
                )
                flights_created += 1
                
                # Also create return flights
                return_departure_hour = random.randint(6, 18)
                return_departure_time = datetime.combine(package.end_date, datetime.min.time().replace(hour=return_departure_hour))
                return_arrival_time = return_departure_time + timedelta(hours=duration_hours)
                
                flight = Flight.objects.create(
                    flight_number=f"{airline[:2].upper()}{random.randint(100, 999)}",
                    airline=airline,
                    departure_city=package.location,
                    arrival_city='Mumbai',  # Return to Mumbai
                    departure_date=package.end_date,
                    departure_time=return_departure_time.time(),
                    arrival_date=package.end_date,
                    arrival_time=return_arrival_time.time(),
                    price=price,
                    available_seats=random.randint(10, 50)
                )
                flights_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {flights_created} flights for {len(packages)} packages'))
