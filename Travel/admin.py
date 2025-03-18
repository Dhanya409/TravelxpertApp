from django import forms
from django.contrib import admin
from django.forms import ModelForm, ValidationError

from .forms import InclusionsExclusionsForm
from .models import DiaryImage, InclusionsExclusions, Itinerary, Passenger, TourPackage, Flight, FlightBooking, Payment, Review, Customer, TravelDiary

class TourPackageAdmin(admin.ModelAdmin):
    # Remove 'slug' from prepopulated_fields if you're not using slug
    # prepopulated_fields = {'slug': ('name',)}  # This line is no longer needed
    list_display = ('name', 'price', 'description')  # Adjust according to your model fields
    search_fields = ('name', 'description')  # You can include other fields here for search

admin.site.register(TourPackage, TourPackageAdmin)
class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = '__all__'  # Include all fields

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    form = ItineraryForm
    list_display = ('tour_package', 'day_number', 'title', 'duration', 'location')
    list_filter = ('tour_package', 'duration')
    search_fields = ('title', 'description', 'location')
    ordering = ('tour_package', 'day_number')

@admin.register(Passenger)

class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'age', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(InclusionsExclusions)
class InclusionsExclusionsAdmin(admin.ModelAdmin):
    list_display = ('tour_package', 'inclusions', 'exclusions')  # Correct field name here
    search_fields = ('tour_package__name',)  # Search by the name of the TourPackage
    list_filter = ('tour_package',)  # Filter by TourPackage

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'departure_city', 'arrival_city', 
                   'departure_date', 'departure_time', 'price', 'available_seats')
    search_fields = ('flight_number', 'airline', 'departure_city', 'arrival_city')
    list_filter = ('airline', 'departure_city', 'arrival_city', 'departure_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_method', 'payment_status', 'payment_date', 'transaction_id')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('transaction_id', 'booking__id')
    readonly_fields = ('payment_date',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.payment_status == 'completed':
            return self.readonly_fields + ('payment_status', 'amount', 'transaction_id', 'booking')
        return self.readonly_fields

@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'flight', 'tour_package', 'total_amount', 'get_payment_status', 'get_passenger_count')
    list_filter = ('flight__airline', 'tour_package')
    search_fields = ('flight__flight_number', 'tour_package__name')
    filter_horizontal = ('passenger',)
    
    def get_payment_status(self, obj):
        try:
            payment = Payment.objects.get(booking=obj)
            return payment.get_payment_status_display()
        except Payment.DoesNotExist:
            return 'Pending Payment'
    get_payment_status.short_description = 'Payment Status'
    
    def get_passenger_count(self, obj):
        return obj.passenger.count()
    get_passenger_count.short_description = 'Passengers'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'review_date', 'get_package_name', 'get_reviewer')
    list_filter = ('rating', 'review_date')
    search_fields = ('booking__tour_package__name', 'review_text')
    readonly_fields = ('review_date',)
    
    def get_package_name(self, obj):
        return obj.booking.tour_package.name
    get_package_name.short_description = 'Package'
    
    def get_reviewer(self, obj):
        return obj.booking.passenger.first().full_name
    get_reviewer.short_description = 'Reviewer'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'user', 'get_date_joined')
    list_filter = ('user__date_joined',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    ordering = ('-user__date_joined',)
    
    def get_date_joined(self, obj):
        return obj.user.date_joined if obj.user else None
    get_date_joined.short_description = 'Date Joined'
    get_date_joined.admin_order_field = 'user__date_joined'


class DiaryImageInline(admin.TabularInline):
    model = DiaryImage
    extra = 1

@admin.register(TravelDiary)
class TravelDiaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)
    inlines = [DiaryImageInline]

@admin.register(DiaryImage)
class DiaryImageAdmin(admin.ModelAdmin):
    list_display = ('diary', 'caption')
    search_fields = ('diary__title', 'caption')



class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tour_package', 'rating', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('user__username', 'tour_package__name')


from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import TourPackage, FlightBooking, Payment, Review
from .views import admin_reports  # Import the report function

class AdminReportsAdmin(admin.ModelAdmin):
    change_list_template = "admin_reports.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('admin_reports/', self.admin_site.admin_view(self.admin_reports_view), name="admin-reports"),
        ]
        return custom_urls + urls

    def admin_reports_view(self, request):
        return admin_reports(request)  # Calls the function from views.py








