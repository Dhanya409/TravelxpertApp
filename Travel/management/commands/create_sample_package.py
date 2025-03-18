from django.core.management.base import BaseCommand
from Travel.models import TourPackage, Itinerary, InclusionsExclusions
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creates a sample Goa tour package'

    def handle(self, *args, **kwargs):
        try:
            # Check if package already exists
            if TourPackage.objects.filter(name="Goa Beach Paradise").exists():
                self.stdout.write(self.style.WARNING('Sample package already exists'))
                return
                
            # Create package
            package = TourPackage.objects.create(
                name="Goa Beach Paradise",
                description="Experience the beautiful beaches of Goa with this amazing package. Includes hotel stay, sightseeing, and water activities.",
                price=29999.00,
                available_slots=20,
                duration="4 days, 3 nights",
                start_date=datetime.now().date() + timedelta(days=7),
                end_date=datetime.now().date() + timedelta(days=10),
                location="Goa",
                highlights="""
                - Stay at a 4-star beach resort
                - Water sports activities included
                - North and South Goa sightseeing
                - Beach hopping tours
                - Evening cruise with dinner
                """,
                is_active=True
            )
            
            # Create itinerary
            itineraries = [
                {
                    'day_number': 1,
                    'title': 'Arrival and North Goa Tour',
                    'description': 'Arrive in Goa, check-in to resort. Evening North Goa tour including Calangute Beach, Fort Aguada, and Candolim Beach.'
                },
                {
                    'day_number': 2,
                    'title': 'Water Sports Day',
                    'description': 'Full day of water sports including parasailing, jet skiing, and banana boat rides at Baga Beach.'
                },
                {
                    'day_number': 3,
                    'title': 'South Goa Exploration',
                    'description': 'Visit the pristine beaches of South Goa including Colva and Palolem. Evening sunset cruise with dinner.'
                },
                {
                    'day_number': 4,
                    'title': 'Departure',
                    'description': 'Free morning for shopping and leisure. Check-out and departure.'
                }
            ]
            
            for itin in itineraries:
                Itinerary.objects.create(
                    tour_package=package,
                    day_number=itin['day_number'],
                    title=itin['title'],
                    description=itin['description']
                )
            
            # Create inclusions/exclusions
            InclusionsExclusions.objects.create(
                tour_package=package,
                inclusions="""
                - 3 nights accommodation in 4-star resort
                - Daily breakfast and dinner
                - All sightseeing and transfers
                - Water sports activities
                - Evening cruise with dinner
                - Professional guide
                - All taxes included
                """,
                exclusions="""
                - Airfare
                - Personal expenses
                - Additional activities
                - Lunch
                - Travel insurance
                """
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created sample package with ID {package.id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample package: {str(e)}')
            )
