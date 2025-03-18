from django.db import models
from django.contrib.auth.models import User  
import time
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.text import slugify
import uuid
from django.utils import timezone
from datetime import timedelta

# Create your models here.
# models.py
from django.db import models

class TourPackage(models.Model):
    CATEGORY_CHOICES = [
        # Destination-Based Packages
        ('domestic', 'Domestic Tours'),
        ('international', 'International Tours'),
        # Theme-Based Packages
        ('adventure', 'Adventure Tours'),
        ('romantic', 'Romantic Getaways'),
        ('family', 'Family Holidays'),
        ('wellness', 'Wellness Retreats'),
        # Budget-Based Packages
        ('budget', 'Budget-Friendly'),
        ('mid_range', 'Mid-Range'),
        ('luxury', 'Luxury Packages'),
    ]

    CATEGORY_GROUPS = {
        'Destination-Based': ['domestic', 'international'],
        'Theme-Based': ['adventure', 'romantic', 'family', 'wellness'],
        'Budget-Based': ['budget', 'mid_range', 'luxury']
    }

    name = models.CharField(max_length=100)  # Name of the package
    description = models.TextField()  # Detailed description of the package
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='domestic')
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the package
    available_slots = models.IntegerField()  # Number of available slots
    duration = models.CharField(max_length=50)  # Duration of the tour (e.g., "5 days, 4 nights")
    start_date = models.DateField()  # Tour start date
    end_date = models.DateField()  # Tour end date
    image = models.ImageField(upload_to='tour_images/')  # Image for the package
    location = models.CharField(max_length=255)  # Tour location
    highlights = models.TextField()  # Key highlights of the tour
    created_at = models.DateTimeField(auto_now_add=True)  # Created timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last updated timestamp
    is_active = models.BooleanField(default=True)  # Whether the package is active or not

    def __str__(self):
        return self.name

    def get_duration(self):
        return f"{self.duration}"

    def get_total_price(self):
        return f"₹ {self.price}"

    class Meta:
        ordering = ['start_date']  # Order packages by start date



class Itinerary(models.Model):
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itineraries')
    day_number = models.IntegerField(default=1)
    title = models.CharField(max_length=200, default='Day Activity')
    description = models.TextField(default='Details will be provided')
    location = models.CharField(max_length=200, default='To be announced')
    duration = models.CharField(max_length=50, default='Full Day')  # e.g., "Full Day", "Half Day"
    meals = models.CharField(max_length=100, default='Breakfast')    # e.g., "Breakfast, Lunch"
    
    class Meta:
        ordering = ['day_number']
    
    def __str__(self):
        return f"Day {self.day_number} - {self.title}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, null=True)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField()  # Replaced dob with age as an integer field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    


class InclusionsExclusions(models.Model):
    tour_package = models.ForeignKey(
        TourPackage, on_delete=models.CASCADE, related_name='inclusions_exclusions'
    )
    inclusions = models.TextField(help_text="List all inclusions for this package")
    exclusions = models.TextField(help_text="List all exclusions for this package")

    def __str__(self):
        return f"Inclusions and Exclusions for {self.tour_package.name}"


class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    airline = models.CharField(max_length=100)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    
    def __str__(self):
        return f"{self.airline} - {self.flight_number}"



class FlightBooking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ]
    
    SEAT_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour_package = models.ForeignKey('TourPackage', on_delete=models.CASCADE)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)
    passenger = models.ManyToManyField('Passenger')
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES, default='economy')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cancellation_reason = models.TextField(null=True, blank=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"
        
    def get_booking_status_display(self):
        return dict(self.BOOKING_STATUS_CHOICES).get(self.booking_status, self.booking_status)
        
    def calculate_refund_amount(self):
        if self.booking_status != 'confirmed':
            return 0
            
        days_until_departure = (self.flight.departure_date - timezone.now().date()).days
        
        if days_until_departure > 7:
            return float(self.total_amount) * 0.90  # 90% refund
        elif days_until_departure > 3:
            return float(self.total_amount) * 0.70  # 70% refund
        elif days_until_departure > 1:
            return float(self.total_amount) * 0.50  # 50% refund
        else:
            return float(self.total_amount) * 0.30  # 30% refund
    
    class Meta:
        ordering = ['-booking_date']  # Orders by most recent bookings by default


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking')
    ]
    
    booking = models.ForeignKey(FlightBooking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_details = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.booking.id}"


class Review(models.Model):
    booking = models.OneToOneField(FlightBooking, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating scale: 1 to 5
    review_text = models.TextField()  # User's review
    review_date = models.DateTimeField(auto_now_add=True)  # Auto timestamp on review creation

    def __str__(self):
        return f"Review for {self.booking.tour_package.name} by {self.booking.user.username}"



class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    booking = models.OneToOneField(FlightBooking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    refund_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"Refund {self.id} - {self.booking.id} - {self.status}"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    

class TravelDiary(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=200)
    travel_date = models.DateField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Travel Diaries'

    def __str__(self):
        return f"{self.title} by {self.user.username}"

class DiaryImage(models.Model):
    diary = models.ForeignKey(TravelDiary, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='diary_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.diary.title}"

class PassportDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey('FlightBooking', on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    passport_expiry = models.DateField()
    issuing_country = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.passenger_name} - {self.passport_number}"

    class Meta:
        verbose_name = "Passport Detail"
        verbose_name_plural = "Passport Details"



class PackingPreferences(models.Model):
    """Model to store user's packing preferences for a booking."""
    booking = models.OneToOneField('FlightBooking', on_delete=models.CASCADE, related_name='packing_preferences', null=True)
    trip_categories = models.JSONField(default=list, null=True)  # List of categories: ['cultural', 'adventure', etc.]
    weather = models.CharField(max_length=20, choices=[
        ('hot', 'Hot'),
        ('moderate', 'Moderate'),
        ('cold', 'Cold'),
        ('rainy', 'Rainy')
    ], default='moderate', null=True)
    traveling_with_kids = models.BooleanField(default=False, null=True)
    special_requirements = models.TextField(blank=True, null=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Packing preferences for {self.booking}"

    def save(self, *args, **kwargs):
        if not self.trip_categories:
            self.trip_categories = ['general']
        super().save(*args, **kwargs)


class PackingList(models.Model):
    """Model to store the actual packing list items."""
    booking = models.OneToOneField('FlightBooking', on_delete=models.CASCADE, related_name='packing_list', null=True)
    preferences = models.OneToOneField('PackingPreferences', on_delete=models.SET_NULL, null=True, related_name='packing_list', blank=True)
    items = models.JSONField(default=dict, null=True)  # Dictionary of categories and their items
    source = models.CharField(max_length=20, default='default', choices=[('gemini', 'AI Generated'), ('default', 'Default List')], null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Packing list for {self.booking}"

class PackingItem(models.Model):
    """Model for individual packing list items."""
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name='packing_items', null=True)
    category = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return f"{self.category}: {self.name}"
    



class LandmarkDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='landmarks/')
    detected_landmark = models.CharField(max_length=255, blank=True, null=True)
    detection_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Landmark Detection - {self.detected_landmark or 'Unknown'}"
    

from django.db import models

class SummarizationRequest(models.Model):
    input_text = models.TextField()
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary (ID: {self.id})"
    
from django.db import models

class TravelChatHistory(models.Model):
    user_query = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query: {self.user_query[:50]}..."






