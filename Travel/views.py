# views.py

from importlib.resources import Package
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse  # Add this import
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from datetime import datetime
import time
from django.shortcuts import render, get_object_or_404
from .models import InclusionsExclusions, Passenger, TourPackage, Flight, FlightBooking, Itinerary, Payment, LandmarkDetection, UserProfile
from .forms import PassengerForm, TourPackageForm, TourPackageUpdateForm, FlightBookingForm, PaymentForm, LandmarkUploadForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from google.cloud import vision
from google.oauth2 import service_account
import tempfile
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import *
from .forms import *
from datetime import datetime
import time
import random
import re
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from decimal import Decimal
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = user.last_login.replace(microsecond=0, tzinfo=None) if user.last_login else ''
        return str(user.pk) + str(timestamp) + str(user.password) + str(login_timestamp)

token_generator = CustomTokenGenerator()

def send_booking_confirmation_email(request, booking):
    """Send booking confirmation email to user"""
    try:
        subject = f'Booking Confirmation - {booking.tour_package.name}'
        from_email = settings.EMAIL_HOST_USER
        to_email = [booking.user.email]
        
        print(f"Sending booking confirmation email to: {to_email}")
        
        # Generate payment URL
        payment_url = request.build_absolute_uri(
            reverse('payment', kwargs={'booking_id': booking.id})
        )
        
        # Prepare context for email template
        context = {
            'booking': booking,
            'payment_url': payment_url,
        }
        
        # Render email templates
        html_content = render_to_string('emails/booking_confirmation_email.html', context)
        text_content = strip_tags(html_content)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
            reply_to=[settings.EMAIL_HOST_USER],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        print("Booking confirmation email sent successfully")
        return True
        
    except Exception as e:
        print(f"Error sending booking confirmation email: {str(e)}")
        return False

def send_payment_confirmation_email(request, booking, payment):
    """Send payment confirmation email to user"""
    try:
        subject = f'Payment Confirmation - {booking.tour_package.name}'
        from_email = settings.EMAIL_HOST_USER
        to_email = [booking.user.email]
        
        print(f"Sending payment confirmation email to: {to_email}")
        
        # Calculate costs
        passenger_count = booking.passenger.count()
        package_cost = Decimal(booking.tour_package.price)
        flight_cost = Decimal(booking.flight.price) * passenger_count
        taxes = (package_cost + flight_cost) * Decimal('0.18')
        
        # Generate URLs for attachments
        ticket_url = request.build_absolute_uri(
            reverse('download_ticket', kwargs={'booking_id': booking.id})
        )
        receipt_url = request.build_absolute_uri(
            reverse('download_receipt', kwargs={'booking_id': booking.id})
        )
        
        # Prepare context for email template
        context = {
            'booking': booking,
            'payment': payment,
            'package_cost': package_cost,
            'flight_cost': flight_cost,
            'taxes': taxes,
            'ticket_url': ticket_url,
            'receipt_url': receipt_url,
        }
        
        # Render email templates
        html_content = render_to_string('emails/payment_confirmation_email.html', context)
        text_content = strip_tags(html_content)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
            reply_to=[settings.EMAIL_HOST_USER],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        print("Payment confirmation email sent successfully")
        return True
        
    except Exception as e:
        print(f"Error sending payment confirmation email: {str(e)}")
        return False

# Create your views here.
from django.shortcuts import render
from .models import TourPackage, Review  # Import the Review model

def index(request):
    packages = TourPackage.objects.all()
    reviews = Review.objects.all()  # Fetch all reviews from the database
    diaries = TravelDiary.objects.filter(visibility='public').order_by('-created_at')[:3]  # Get 3 most recent public diaries

    # Get unique categories for the dropdown
    categories = TourPackage.objects.values_list('category', flat=True).distinct()

    # Get filter parameters
    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    # Apply filters
    if search_query:
        packages = packages.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category:
        packages = packages.filter(category__iexact=category)

    if min_price:
        try:
            min_price = float(min_price)
            packages = packages.filter(price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            max_price = float(max_price)
            packages = packages.filter(price__lte=max_price)
        except ValueError:
            pass

    context = {
        'packages': packages,
        'categories': categories,
        'reviews': reviews,
        'diaries': diaries,
        'selected_category': category,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'search_query': search_query
    }
    
    return render(request, 'index.html', context)


def about(request):
    context = {
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    }
    return render(request, 'about.html', context)

def destination(request):
    return render(request, 'destination.html')  

def hotel(request):
    return render(request, 'hotel.html')  

def blog(request):
    context = {
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    }
    return render(request, 'blog.html', context)

def contact(request):
    context = {
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    }
    return render(request, 'contact.html', context)


# Admin views

def admin_tour_package_page(request):
    packages = TourPackage.objects.all()
    return render(request, 'admin_tour_package_page.html', {'packages': packages})

def tour_package_add(request):
    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_tour_package_page')  # Redirect to a success page after adding the package
    else:
        form = TourPackageForm()
    return render(request, 'add_tour_package.html', {'form': form})

def tour_package_update(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        form = TourPackageUpdateForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            return redirect('admin_tour_package_page')  # Redirect to the package list page after updating
    else:
        form = TourPackageUpdateForm(instance=package)
    return render(request, 'update_tour_package.html', {'form': form, 'package': package})

def tour_package_delete(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        package.delete()
        return redirect('admin_tour_package_page')  # Redirect to the package list page after deletion
    return render(request, 'delete_tour_package.html', {'package': package})

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                auth_login(request, user)
                return redirect('admin_tour_package_page')
            else:
                return render(request, 'admin_login.html', {'form': form, 'error_message': 'Invalid credentials'})

    else:
        form = AuthenticationForm() # type: ignore

    return render(request, 'admin_login.html', {'form': form})


def package_detail(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)  
    is_available = package.available_slots > 0
    return render(request, 'package_detail.html', {
        'package': package,
        'is_available': is_available
    })

def tour_packages(request):
    packages = TourPackage.objects.all()
    return render(request, 'packages.html', {
        'packages': packages,
        'page_title': 'Tour Packages'
    })



from django.shortcuts import render, get_object_or_404
from .models import TourPackage, Itinerary
from django.shortcuts import render, get_object_or_404
from .models import TourPackage

def itinerary_overview(request, package_id):
    # Fetch the tour package and its associated itineraries
    tour_package = get_object_or_404(TourPackage, id=package_id)
    itineraries = tour_package.itineraries.all()  # Related_name 'itineraries' is used here

    # Pass context data to the template
    context = {
        'tour_package': tour_package,
        'itineraries': itineraries,
    }

    return render(request, 'itinerary_overview.html', context)


# --------- AUTHENTICATION AND AUTHORIZATION SECTION ---------

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from google.cloud import vision
from google.oauth2 import service_account
import tempfile
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import User, Customer
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import Customer
from django.db.models import Q

from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Check if username and password are not empty
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')  # Re-render the form with an error message
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next', 'index')  # Redirect to next page or index
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('index')

def is_password_strong(password):
    """
    Check if the password meets strength requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False
    return True

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate required fields
        if not all([first_name, last_name, username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        # Validate password strength
        if not is_password_strong(password):
            messages.error(request, 'Password must be at least 8 characters long and contain uppercase, lowercase, digits, and special characters.')
            return render(request, 'register.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'register.html')

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, f'Account created for {username}! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'register.html')

    return render(request, 'register.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            
            # Fix: Use reverse to generate the correct URL
            reset_url = reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            reset_password_url = request.build_absolute_uri(reset_url)
            
            email_subject = 'Reset Your Password'

            # Render both HTML and plain text versions of the email
            email_body_html = render_to_string('reset_password_email.html', {
                'reset_password_url': reset_password_url,
                'user': user,
            })
            email_body_text = "Click the following link to reset your password: {}".format(reset_password_url)

            # Create an EmailMultiAlternatives object to send both HTML and plain text versions
            email = EmailMultiAlternatives(
                email_subject,
                email_body_text,
                settings.EMAIL_HOST_USER,
                [email],
            )
            email.attach_alternative(email_body_html, 'text/html')  # Attach HTML version
            email.send(fail_silently=False)

            messages.success(request, 'An email has been sent to your email address with instructions on how to reset your password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'reset_password.html')

            if not is_password_strong(password):
                messages.error(request, "Password is not strong enough. Please ensure it has at least 8 characters, including uppercase, lowercase, numbers, and special characters.")
                return render(request, 'reset_password.html')

            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been reset successfully! Please login with your new password.")
            return redirect('login')
        return render(request, 'reset_password.html')
    else:
        messages.error(request, "The password reset link is invalid or has expired!")
        return redirect('login')
    

    # ________________________________________________________________________________________________________________

from django.shortcuts import render, redirect
from .models import Passenger
from .models import TravelDiary
from .forms import TravelDiaryForm

@login_required
def passenger_details(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)
    
    if request.method == 'POST':
        # Get all passenger data from the form
        full_names = request.POST.getlist('full_name[]')
        emails = request.POST.getlist('email[]')
        phones = request.POST.getlist('phone[]')
        ages = request.POST.getlist('age[]')
        
        # Validate that we have at least one passenger
        if not full_names:
            messages.error(request, 'Please provide at least one passenger\'s details')
            return render(request, 'passenger_details.html', {'package': package})
        
        # Create a list to store passenger IDs
        passenger_ids = []
        
        try:
            # Create passenger objects for each set of details
            for i in range(len(full_names)):
                # Ensure phone number is exactly 10 digits
                if not phones[i].isdigit() or len(phones[i]) != 10:
                    messages.error(request, f'Phone number for passenger {i + 1} must be exactly 10 digits.')
                    return render(request, 'passenger_details.html', {'package': package})
                
                # Ensure email contains '@'
                if '@' not in emails[i]:
                    messages.error(request, f'Email for passenger {i + 1} is invalid. Please provide a valid email address.')
                    return render(request, 'passenger_details.html', {'package': package})
                
                # Ensure age is greater than 0
                if not ages[i].isdigit() or int(ages[i]) <= 0:
                    messages.error(request, f'Age for passenger {i + 1} must be greater than 0.')
                    return render(request, 'passenger_details.html', {'package': package})
                
                passenger = Passenger.objects.create(
                    user=request.user,  # Link passenger to the current user
                    full_name=full_names[i],
                    email=emails[i],
                    phone=phones[i],
                    age=int(ages[i])
                )
                passenger_ids.append(passenger.id)
            
            # Store passenger IDs and count in session
            request.session['passenger_ids'] = passenger_ids
            request.session['passenger_count'] = len(passenger_ids)
            
            # Redirect to select flight page
            return redirect('select_flight', package_id=package_id)
            
        except Exception as e:
            messages.error(request, f'Error saving passenger details: {str(e)}')
            return render(request, 'passenger_details.html', {'package': package})
    
    return render(request, 'passenger_details.html', {'package': package})




def package_service(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)
    # Query the inclusions and exclusions related to this package
    inclusions_exclusions = InclusionsExclusions.objects.filter(tour_package=package)
    return render(request, 'package_service.html', {
        'package': package,
        'inclusions_exclusions': inclusions_exclusions
    })




@login_required
def booking_confirmation(request, booking_id):
    try:
        # Get booking with all related data
        booking = FlightBooking.objects.select_related(
            'tour_package', 
            'flight', 
            'user'
        ).prefetch_related(
            'passenger',
            'payments'
        ).get(id=booking_id, user=request.user)
        
        # Get the payment
        payment = booking.payments.filter(payment_status='completed').first()
        
        if not payment:
            messages.warning(request, 'Payment not found for this booking.')
            return redirect('payment', booking_id=booking_id)
        
        context = {
            'booking': booking,
            'payment': payment,
            'title': 'Booking Confirmation',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        return render(request, 'booking_confirmation.html', context)
        
    except FlightBooking.DoesNotExist:
        messages.error(request, 'Booking not found or you do not have permission to view it.')
        return redirect('my_bookings')
    except Exception as e:
        messages.error(request, f'Error accessing booking details: {str(e)}')
        return redirect('my_bookings')

@login_required
def select_flight(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id)
    
    # Filter flights based on arrival city (package location), dates, and available seats
    available_flights = Flight.objects.filter(
        arrival_city=package.location,  
        departure_date=package.start_date,
        available_seats__gte=1
    )
    
    if not available_flights:
        messages.warning(request, 'No flights available for your selected date and destination. Please try different dates or contact our support.')
    
    return render(request, 'select_flight.html', {
        'flights': available_flights,
        'package': package
    })

@login_required
def process_booking(request, flight_id, package_id):
    flight = get_object_or_404(Flight, id=flight_id)
    package = get_object_or_404(TourPackage, id=package_id)
    
    # Get passenger IDs from session
    passenger_ids = request.session.get('passenger_ids', [])
    passenger_count = len(passenger_ids)
    
    if not passenger_ids:
        messages.error(request, 'No passenger details found. Please try booking again.')
        return redirect('passenger_details', package_id=package_id)
    
    # Check if enough seats are available
    if flight.available_seats < passenger_count:
        messages.error(request, 'Not enough seats available for all passengers.')
        return redirect('select_flight', package_id=package_id)
    
    # Check if enough package slots are available
    if package.available_slots < 1:  # One slot per booking
        messages.error(request, 'This package is no longer available.')
        return redirect('packages')
    
    try:
        # Create the booking
        booking = FlightBooking.objects.create(
            user=request.user,
            flight=flight,
            tour_package=package,
            seat_class='economy',
            booking_status='pending',
            total_amount=flight.price * passenger_count  # Multiply by passenger count
        )
        
        # Add passengers to the booking
        passengers = Passenger.objects.filter(id__in=passenger_ids)
        booking.passenger.add(*passengers)
        
        # Send booking confirmation email
        send_booking_confirmation_email(request, booking)
        
        # Clear session data
        request.session.pop('passenger_ids', None)
        request.session.pop('passenger_count', None)
        
        # Store booking ID in session for payment process
        request.session['booking_id'] = booking.id
        
        messages.success(request, 'Booking created successfully! Please proceed with payment.')
        return redirect('payment', booking_id=booking.id)
        
    except Exception as e:
        messages.error(request, f'Error creating booking: {str(e)}')
        return redirect('select_flight', package_id=package_id)

@login_required
def payment(request, booking_id):
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        
        # Check if payment already exists
        existing_payment = Payment.objects.filter(booking=booking, payment_status='completed').exists()
        if existing_payment:
            messages.info(request, 'Payment has already been completed for this booking.')
            return redirect('booking_confirmation', booking_id=booking_id)
        
        # Get passenger count
        passenger_count = booking.passenger.count()
        
        # Calculate total amount including passenger count
        package_cost = Decimal(booking.tour_package.price)
        flight_cost = Decimal(booking.flight.price) * passenger_count
        taxes = (package_cost + flight_cost) * Decimal('0.18')  # 18% GST
        total_amount = package_cost + flight_cost + taxes
        
        # Update booking with total amount
        booking.total_amount = total_amount
        booking.save()
        
        context = {
            'booking': booking,
            'package_cost': package_cost,
            'flight_cost': flight_cost,
            'taxes': taxes,
            'total_amount': total_amount,
            'title': 'Payment',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        return render(request, 'payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading payment page: {str(e)}')
        return redirect('my_bookings')

@login_required
def process_payment(request, booking_id):
    if request.method != 'POST':
        return redirect('payment', booking_id=booking_id)
    
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            messages.error(request, 'Please select a payment method')
            return redirect('payment', booking_id=booking_id)
        
        # Check if payment already exists
        existing_payment = Payment.objects.filter(booking=booking, payment_status='completed').exists()
        if existing_payment:
            messages.info(request, 'Payment has already been completed for this booking.')
            return redirect('booking_confirmation', booking_id=booking_id)
        
        # Get passenger count
        passenger_count = booking.passenger.count()
        
        # Calculate total amount including passenger count
        package_cost = Decimal(booking.tour_package.price)
        flight_cost = Decimal(booking.flight.price) * passenger_count
        taxes = (package_cost + flight_cost) * Decimal('0.18')  # 18% GST
        total_amount = package_cost + flight_cost + taxes
        
        # Generate a unique transaction ID
        transaction_id = f'TXN{int(time.time())}{random.randint(1000,9999)}'
        
        # Get additional payment details based on method
        payment_details = {}
        
        if payment_method == 'upi':
            upi_id = request.POST.get('upiId')
            if not upi_id:
                messages.error(request, 'Please enter UPI ID')
                return redirect('payment', booking_id=booking_id)
            payment_details['upi_id'] = upi_id
            payment_details['payment_type'] = 'UPI'
            
        elif payment_method in ['credit_card', 'debit_card']:
            card_number = request.POST.get('cardNumber', '').strip()
            card_expiry = request.POST.get('expiryDate', '').strip()
            card_cvv = request.POST.get('cvv', '').strip()
            card_name = request.POST.get('cardName', '').strip()
            
            if not all([card_number, card_expiry, card_cvv, card_name]):
                messages.error(request, 'Please fill in all card details')
                return redirect('payment', booking_id=booking_id)
            
            # Store last 4 digits only for security
            payment_details['card_last4'] = card_number[-4:]
            payment_details['card_name'] = card_name
            payment_details['card_type'] = payment_method
            
        elif payment_method == 'net_banking':
            bank = request.POST.get('bankSelect')
            if not bank:
                messages.error(request, 'Please select a bank')
                return redirect('payment', booking_id=booking_id)
            payment_details['bank'] = bank
        
        try:
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=total_amount,
                payment_method=payment_method,
                payment_status='completed',
                transaction_id=transaction_id,
                payment_date=timezone.now(),
                payment_details=payment_details
            )
            
            # Update booking status and total amount
            booking.booking_status = 'confirmed'
            booking.total_amount = total_amount
            booking.save()

            # Reduce package availability
            tour_package = booking.tour_package
            tour_package.available_slots = max(0, tour_package.available_slots - 1)
            tour_package.save()

            # Reduce flight seat availability
            flight = booking.flight
            flight.available_seats = max(0, flight.available_seats - passenger_count)
            flight.save()
            
            # Send payment confirmation email
            send_payment_confirmation_email(request, booking, payment)
            
            messages.success(request, 'Payment successful! Your booking has been confirmed.')
            return redirect('booking_confirmation', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('payment', booking_id=booking_id)
        
    except FlightBooking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('payment', booking_id=booking_id)

@login_required
def my_bookings(request):
    try:
        # Get all bookings for the current user with related data
        bookings = FlightBooking.objects.select_related(
            'tour_package',
            'flight',
            'user'
        ).prefetch_related(
            'passenger',
            'payments'
        ).filter(
            user=request.user
        ).order_by('-booking_date')  # Most recent first
        
        # Prepare booking data with payment info
        booking_data = []
        for booking in bookings:
            # Get the latest payment for this booking
            payment = booking.payments.filter(payment_status='completed').first()
            
            booking_info = {
                'booking': booking,
                'payment': payment,
                'status_class': 'success' if booking.booking_status == 'confirmed' else 'warning'
            }
            booking_data.append(booking_info)
        
        context = {
            'booking_data': booking_data,
            'title': 'My Bookings',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        
        return render(request, 'my_bookings.html', context)
        
    except Exception as e:
        messages.error(request, f'Error retrieving bookings: {str(e)}')
        return render(request, 'my_bookings.html', {'booking_data': [], 'title': 'My Bookings'})

@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking, payment_status='completed')
    
    # Create the PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Container for elements
    elements = []

    # Title
    elements.append(Paragraph("TravelXpert", title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("E-Ticket / Booking Confirmation", heading_style))
    elements.append(Spacer(1, 20))
    
    # Booking Details
    elements.append(Paragraph("Booking Details", heading_style))
    booking_data = [
        ['Booking ID:', str(booking.id)],
        ['Booking Date:', booking.booking_date.strftime('%d %b %Y')],
        ['Booking Status:', booking.get_booking_status_display()],
        ['Transaction ID:', payment.transaction_id],
    ]
    booking_table = Table(booking_data, colWidths=[150, 350])
    booking_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 20))
    
    # Package Details
    elements.append(Paragraph("Package Details", heading_style))
    package_data = [
        ['Package Name:', booking.tour_package.name],
        ['Duration:', booking.tour_package.duration],
        ['Start Date:', booking.tour_package.start_date.strftime('%d %b %Y')],
        ['End Date:', booking.tour_package.end_date.strftime('%d %b %Y')],
        ['Location:', booking.tour_package.location],
    ]
    package_table = Table(package_data, colWidths=[150, 350])
    package_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(package_table)
    elements.append(Spacer(1, 20))
    
    # Flight Details
    elements.append(Paragraph("Flight Details", heading_style))
    flight_data = [
        ['Flight Number:', booking.flight.flight_number],
        ['Airline:', booking.flight.airline],
        ['From:', booking.flight.departure_city],
        ['To:', booking.flight.arrival_city],
        ['Departure:', f"{booking.flight.departure_date.strftime('%d %b %Y')} {booking.flight.departure_time}"],
        ['Arrival:', f"{booking.flight.arrival_date.strftime('%d %b %Y')} {booking.flight.arrival_time}"],
    ]
    flight_table = Table(flight_data, colWidths=[150, 350])
    flight_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(flight_table)
    elements.append(Spacer(1, 20))
    
    # Passenger Details
    elements.append(Paragraph("Passenger Details", heading_style))
    passenger_data = [['Full Name', 'Email', 'Phone', 'Age']]
    for passenger in booking.passenger.all():
        passenger_data.append([
            passenger.full_name,
            passenger.email,
            passenger.phone,
            str(passenger.age)
        ])
    passenger_table = Table(passenger_data, colWidths=[150, 150, 100, 100])
    passenger_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(passenger_table)
    elements.append(Spacer(1, 20))
    
    # Payment Details
    elements.append(Paragraph("Payment Details", heading_style))
    payment_data = [
        ['Amount Paid:', f"₹{payment.amount}"],
        ['Payment Method:', payment.get_payment_method_display()],
        ['Payment Status:', payment.get_payment_status_display()],
        ['Transaction ID:', payment.transaction_id],
    ]
    payment_table = Table(payment_data, colWidths=[150, 350])
    payment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(payment_table)
    
    # Build the PDF document
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and create the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    response.write(pdf)
    
    return response


@login_required
def view_itinerary(request, booking_id):
    try:
        booking = FlightBooking.objects.get(id=booking_id)
        tour_package = booking.tour_package
        itineraries = tour_package.itineraries.all().order_by('day_number')
        
        context = {
            'booking': booking,
            'tour_package': tour_package,
            'itineraries': itineraries,
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        return render(request, 'itinerary.html', context)
        
    except FlightBooking.DoesNotExist:
        messages.error(request, 'Booking not found')
        return redirect('index')
    except Exception as e:
        messages.error(request, f'Error viewing itinerary: {str(e)}')
        return redirect('index')

@login_required
def my_bookings(request):
    try:
        # Get all bookings for the current user with related data
        bookings = FlightBooking.objects.select_related(
            'tour_package',
            'flight',
            'user'
        ).prefetch_related(
            'passenger',
            'payments'
        ).filter(
            user=request.user
        ).order_by('-booking_date')  # Most recent first
        
        # Prepare booking data with payment info
        booking_data = []
        for booking in bookings:
            # Get the latest payment for this booking
            payment = booking.payments.filter(payment_status='completed').first()
            
            booking_info = {
                'booking': booking,
                'payment': payment,
                'status_class': 'success' if booking.booking_status == 'confirmed' else 'warning'
            }
            booking_data.append(booking_info)
        
        context = {
            'booking_data': booking_data,
            'title': 'My Bookings',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        
        return render(request, 'my_bookings.html', context)
        
    except Exception as e:
        messages.error(request, f'Error retrieving bookings: {str(e)}')
        return render(request, 'my_bookings.html', {'booking_data': [], 'title': 'My Bookings'})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason')
        if not reason:
            messages.error(request, 'Please provide a reason for cancellation.')
            return redirect('cancel_booking', booking_id=booking_id)
        
        if booking.booking_status != 'cancelled':
            # Calculate refund amount
            refund_amount = booking.calculate_refund_amount()
            
            # Update booking
            booking.booking_status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancellation_date = timezone.now()
            booking.refund_amount = refund_amount
            booking.save()
            
            # Update flight seats
            flight = booking.flight
            flight.available_seats += 1  # Assuming 1 seat per booking
            flight.save()
            
            messages.success(request, f'Your booking has been cancelled. Refund amount: ₹{refund_amount}')
        else:
            messages.warning(request, 'This booking is already cancelled.')
        
        return redirect('my_bookings')
    
    return render(request, 'cancel_booking.html', {
        'booking': booking,
        'refund_amount': booking.calculate_refund_amount(),
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    })

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

@login_required
def generate_ticket(request, booking_id):
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        
        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph('E-Ticket', styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Booking Details
        elements.append(Paragraph('Booking Details', styles['Heading2']))
        elements.append(Paragraph(f'Booking ID: {booking.id}', styles['Normal']))
        elements.append(Paragraph(f'Booking Date: {booking.booking_date.strftime("%d %b %Y")}', styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Flight Details
        elements.append(Paragraph('Flight Details', styles['Heading2']))
        flight_data = [
            ['Airline', booking.flight.airline],
            ['Flight Number', booking.flight.flight_number],
            ['From', booking.flight.departure_city],
            ['To', booking.flight.arrival_city],
            ['Date', booking.flight.departure_date.strftime('%d %b %Y')],
            ['Time', booking.flight.departure_time.strftime('%H:%M')],
            ['Class', booking.get_seat_class_display()]
        ]
        flight_table = Table(flight_data)
        flight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(flight_table)
        elements.append(Spacer(1, 20))
        
        # Passenger Details
        elements.append(Paragraph('Passenger Details', styles['Heading2']))
        passenger_data = [['Name', 'Age', 'Gender', 'ID Type', 'ID Number']]
        for passenger in booking.passenger.all():
            passenger_data.append([
                passenger.name,
                str(passenger.age),
                passenger.gender,
                passenger.id_type,
                passenger.id_number
            ])
        passenger_table = Table(passenger_data)
        passenger_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(passenger_table)
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph('This is a computer-generated document. No signature is required.', styles['Normal']))
        elements.append(Paragraph('For any assistance, please contact our 24/7 helpline: 1800-XXX-XXXX', styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        # Generate response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating ticket: {str(e)}')
        return redirect('my_bookings')

@login_required
def generate_bill(request, booking_id):
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        payment = booking.payments.first()
        
        if not payment:
            messages.error(request, 'No payment found for this booking')
            return redirect('my_bookings')
        
        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph('TravelXpert Invoice', styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Company Details
        elements.append(Paragraph('TravelXpert', styles['Heading1']))
        elements.append(Paragraph('Your Trusted Travel Partner', styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Customer Details
        elements.append(Paragraph('Bill To:', styles['Heading2']))
        elements.append(Paragraph(f'Name: {booking.user.get_full_name()}', styles['Normal']))
        elements.append(Paragraph(f'Email: {booking.user.email}', styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Bill Details
        elements.append(Paragraph('Bill Details', styles['Heading2']))
        subtotal = Decimal(booking.tour_package.price) + Decimal(booking.flight.price)
        gst = subtotal * Decimal('0.18')
        total = subtotal + gst
        
        bill_data = [
            ['Description', 'Amount'],
            ['Tour Package', f'₹{booking.tour_package.price:,.2f}'],
            ['Flight Ticket', f'₹{booking.flight.price:,.2f}'],
            ['Subtotal', f'₹{subtotal:,.2f}'],
            ['GST (18%)', f'₹{gst:,.2f}'],
            ['Total Amount', f'₹{total:,.2f}']
        ]
        bill_table = Table(bill_data)
        bill_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        elements.append(bill_table)
        elements.append(Spacer(1, 20))
        
        # Payment Details
        elements.append(Paragraph('Payment Information', styles['Heading2']))
        payment_data = [
            ['Transaction ID', payment.transaction_id],
            ['Payment Method', payment.get_payment_method_display()],
            ['Payment Date', payment.payment_date.strftime('%d %b %Y')],
            ['Status', payment.get_payment_status_display()]
        ]
        payment_table = Table(payment_data)
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(payment_table)
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph('This is a computer-generated document. No signature is required.', styles['Normal']))
        elements.append(Paragraph('Thank you for choosing TravelXpert!', styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Generate response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{booking.id}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating bill: {str(e)}')
        return redirect('my_bookings')
@login_required
def download_receipt(request, booking_id):
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        payment = booking.payments.first()  # Get the first payment for this booking
        
        if not payment:
            messages.error(request, 'No payment found for this booking')
            return redirect('my_bookings')

        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph('Payment Receipt', title_style))
        elements.append(Spacer(1, 20))

        # Customer Details
        elements.append(Paragraph('Customer Details', styles['Heading2']))
        current_date = timezone.now().strftime('%B %d, %Y')
        
        # Get lead passenger if available
        lead_passenger = booking.passenger.first() if hasattr(booking, 'passenger') else None
        
        customer_data = [
            ['Name', booking.user.username],
            ['Email', booking.user.email],
            ['Date', current_date],
            ['Transaction ID', str(payment.id)]
        ]
        
        # Add lead passenger info if available
        if lead_passenger:
            customer_data.append(['Lead Passenger', lead_passenger.full_name])  # Updated from 'name' to 'full_name'
            customer_data.append(['Total Passengers', str(booking.passenger.count())])
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([  
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 20))

        # Package Details
        elements.append(Paragraph('Package Details', styles['Heading2']))
        package_data = [
            ['Package Name:', booking.tour_package.name],
            ['Flight', f"{booking.flight.airline} - {booking.flight.flight_number}"],
            ['From', booking.flight.departure_city],
            ['To', booking.flight.arrival_city],
            ['Date', booking.flight.departure_date.strftime('%B %d, %Y')],
            ['Time', booking.flight.departure_time.strftime('%I:%M %p')]
        ]

        package_table = Table(package_data, colWidths=[2*inch, 4*inch])
        package_table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(package_table)
        elements.append(Spacer(1, 20))

        # Calculate taxes
        tax_breakdown = calculate_taxes(booking)

        # Payment Details
        elements.append(Paragraph('Payment Details', styles['Heading2']))
        payment_data = [
            ['Description', 'Amount'],
            ['Package Cost', f'₹{booking.tour_package.price:,.2f}'],
            ['Flight Cost', f'₹{booking.flight.price:,.2f}'],
            ['Subtotal', f'₹{tax_breakdown["subtotal"]:,.2f}'],
            ['Package GST (18%)', f'₹{tax_breakdown["package_gst"]:,.2f}'],
            ['Flight GST (18%)', f'₹{tax_breakdown["flight_gst"]:,.2f}'],
            ['Service Charge (5%)', f'₹{tax_breakdown["service_charge"]:,.2f}'],
            ['Convenience Fee', f'₹{tax_breakdown["convenience_fee"]:,.2f}'],
            ['Total Amount', f'₹{payment.amount:,.2f}']
        ]
        payment_table = Table(payment_data, colWidths=[3*inch, 3*inch])
        payment_table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 30))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            textColor=colors.HexColor('#6c757d'),
            fontSize=8,
            alignment=1
        )
        elements.append(Paragraph('This is a computer-generated document. No signature is required.', footer_style))
        elements.append(Paragraph('Thank you for choosing TravelXpert!', footer_style))

        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        # Generate response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{booking.id}.pdf"'
        response.write(pdf)

        return response

    except Exception as e:
        messages.error(request, f'Error generating receipt: {str(e)}')
        return redirect('my_bookings')


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
    
    # Calculate subtotal and taxes
    subtotal = booking.tour_package.price + booking.flight.price
    taxes = round(subtotal * Decimal('0.18'), 2)  # 18% GST
    
    context = {
        'booking': booking,
        'subtotal': subtotal,
        'taxes': taxes,
    }
    
    return render(request, 'payment_receipt.html', context)

@login_required
def packages_by_category(request, category):
    packages = TourPackage.objects.filter(category=category, is_active=True).order_by('start_date')
    category_display_name = dict(TourPackage.CATEGORY_CHOICES)[category]
    
    # Get the category group (Destination-Based, Theme-Based, or Budget-Based)
    category_group = next(
        (group for group, cats in TourPackage.CATEGORY_GROUPS.items() if category in cats),
        'All Packages'
    )
    
    context = {
        'packages': packages,
        'category': category,
        'category_display_name': category_display_name,
        'category_group': category_group,
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    }
    return render(request, 'packages_by_category.html', context)

@login_required
def dashboard(request):
    # Get user's bookings
    bookings = FlightBooking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Get total amount spent
    total_spent = sum(booking.total_amount for booking in bookings)
    
    # Get upcoming trips
    upcoming_trips = bookings.filter(
        tour_package__start_date__gte=timezone.now()
    ).order_by('tour_package__start_date')
    
    # Get completed trips
    completed_trips = bookings.filter(
        tour_package__end_date__lt=timezone.now()
    ).order_by('-tour_package__end_date')
    
    context = {
        'bookings': bookings,
        'total_spent': total_spent,
        'upcoming_trips': upcoming_trips,
        'completed_trips': completed_trips,
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    }
    return render(request, 'dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Update user details
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')
    
    # Get or create user profile for display
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'user_profile': profile
    }
    return render(request, 'edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the old password is correct
        if not request.user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
            return redirect('dashboard')

        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('dashboard')

        # Check password strength
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('dashboard')

        # Change the password
        request.user.set_password(new_password)
        request.user.save()

        # Update the session to prevent logout
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('dashboard')

    return render(request, 'change_password.html', {
        'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
    })

@login_required
def create_sample_package(request):
    try:
        # Create sample packages with different destinations
        packages = [
            {
                'name': "Goa Beach Paradise",
                'description': "Experience the sun, sand, and vibrant culture of Goa. Enjoy pristine beaches, water sports, delicious seafood, and vibrant nightlife.",
                'price': 25000,
                'available_slots': 20,
                'duration': 5,
                'start_date': "2024-01-15",
                'end_date': "2024-01-20",
                'location': "Goa",
                'highlights': "Beautiful beaches, Water sports, Nightlife, Local cuisine",
                'image_url': "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?ixlib=rb-4.0.3",
                'category': 'beach'
            },
            {
                'name': "Kerala Backwaters",
                'description': "Explore the serene backwaters and lush landscapes of Kerala. Stay in luxury houseboats, experience Ayurvedic treatments, and visit tea plantations.",
                'price': 35000,
                'available_slots': 15,
                'duration': 6,
                'start_date': "2024-01-20",
                'end_date': "2024-01-26",
                'location': "Kerala",
                'highlights': "Houseboat stay, Ayurveda spa, Tea plantations, Cultural shows",
                'image_url': "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?ixlib=rb-4.0.3",
                'category': 'nature'
            },
            {
                'name': "Rajasthan Heritage Tour",
                'description': "Discover the royal heritage and majestic forts of Rajasthan. Experience desert safaris, traditional music, and authentic Rajasthani cuisine.",
                'price': 45000,
                'available_slots': 18,
                'duration': 7,
                'start_date': "2024-02-01",
                'end_date': "2024-02-08",
                'location': "Rajasthan",
                'highlights': "Palace visits, Desert safari, Folk music, Traditional cuisine",
                'image_url': "https://images.unsplash.com/photo-1599661046289-e31897846e41?ixlib=rb-4.0.3",
                'category': 'cultural'
            },
            {
                'name': "Manali Adventure",
                'description': "Experience thrilling adventures in the snow-capped mountains of Manali. Perfect for adventure enthusiasts and nature lovers.",
                'price': 30000,
                'available_slots': 25,
                'duration': 5,
                'start_date': "2024-02-10",
                'end_date': "2024-02-15",
                'location': "Manali",
                'highlights': "Skiing, Paragliding, River rafting, Mountain trekking",
                'image_url': "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?ixlib=rb-4.0.3",
                'category': 'adventure'
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
                highlights=package_data['highlights'],
                image_url=package_data['image_url'],
                category=package_data['category']
            )
            
            # Create inclusions/exclusions for each package
            InclusionsExclusions.objects.create(
                tour_package=package,
                inclusions="""
                - Luxury hotel accommodation (4/5 star)
                - Daily breakfast and dinner
                - All transfers and sightseeing as per itinerary
                - Professional tour guide
                - All applicable taxes
                - Travel insurance
                - Welcome drink on arrival
                """,
                exclusions="""
                - Airfare/Train fare
                - Personal expenses and tips
                - Optional activities not in itinerary
                - Lunch and beverages
                - Visa charges if applicable
                - Any items not mentioned in inclusions
                """
            )
            
            # Create sample itinerary
            Itinerary.objects.create(
                tour_package=package,
                day_number=1,
                title=f"Welcome to {package.location}",
                description=f"""
                Arrive at {package.location} airport/railway station
                Transfer to hotel and check-in
                Welcome drink and orientation
                Evening free for leisure
                Dinner at hotel
                """
            )
            
            Itinerary.objects.create(
                tour_package=package,
                day_number=2,
                title="Local Sightseeing",
                description=f"""
                Breakfast at hotel
                Full day local sightseeing
                Visit to major attractions
                Evening cultural activities
                Dinner at hotel
                """
            )
            
            # Create sample flights for each package
            flights = [
                {
                    'airline': "Air India",
                    'flight_number': f"AI{package.id}01",
                    'departure_city': "Mumbai",
                    'price': 5000.00,
                    'available_seats': 50
                },
                {
                    'airline': "IndiGo",
                    'flight_number': f"6E{package.id}02",
                    'departure_city': "Delhi",
                    'price': 4500.00,
                    'available_seats': 45
                },
                {
                    'airline': "SpiceJet",
                    'flight_number': f"SG{package.id}03",
                    'departure_city': "Bangalore",
                    'price': 5500.00,
                    'available_seats': 40
                }
            ]
            
            for flight_data in flights:
                Flight.objects.create(
                    flight_number=flight_data['flight_number'],
                    airline=flight_data['airline'],
                    departure_city=flight_data['departure_city'],
                    arrival_city=package.location,
                    departure_date=package.start_date,
                    departure_time="10:00",
                    arrival_date=package.start_date,
                    arrival_time="12:00",
                    price=flight_data['price'],
                    available_seats=flight_data['available_seats']
                )
        
        messages.success(request, "Sample packages, flights, and itineraries created successfully!")
        return redirect('packages')
        
    except Exception as e:
        messages.error(request, f"Error creating sample packages: {str(e)}")
        return redirect('packages')

@login_required
def add_multiple_flights(request):
    try:
        # Get all tour packages
        packages = TourPackage.objects.all()
        
        # List of major cities
        departure_cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
            'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Kochi'
        ]
        
        # List of airlines
        airlines = [
            ('Air India', 'AI'),
            ('IndiGo', '6E'),
            ('SpiceJet', 'SG'),
            ('Vistara', 'UK'),
            ('Go First', 'G8')
        ]
        
        for package in packages:
            # Create flights from each departure city
            for city in departure_cities:
                # Skip if city is same as destination
                if city.lower() == package.location.lower():
                    continue
                
                # Create flights for each airline
                for airline_name, airline_code in airlines:
                    # Morning flight
                    Flight.objects.get_or_create(
                        flight_number=f'{airline_code}{package.id}M{departure_cities.index(city)}',
                        defaults={
                            'airline': airline_name,
                            'departure_city': city,
                            'arrival_city': package.location,
                            'departure_date': package.start_date,
                            'departure_time': '08:00',
                            'arrival_date': package.start_date,
                            'arrival_time': '10:00',
                            'price': 5000 + (departure_cities.index(city) * 500),  # Price varies by city
                            'available_seats': 50
                        }
                    )
                    
                    # Evening flight
                    Flight.objects.get_or_create(
                        flight_number=f'{airline_code}{package.id}E{departure_cities.index(city)}',
                        defaults={
                            'airline': airline_name,
                            'departure_city': city,
                            'arrival_city': package.location,
                            'departure_date': package.start_date,
                            'departure_time': '18:00',
                            'arrival_date': package.start_date,
                            'arrival_time': '20:00',
                            'price': 4500 + (departure_cities.index(city) * 500),  # Evening flights slightly cheaper
                            'available_seats': 50
                        }
                    )
        
        messages.success(request, "Additional flights added successfully!")
        return redirect('packages')
        
    except Exception as e:
        messages.error(request, f"Error adding flights: {str(e)}")
        return redirect('packages')

@login_required
def add_sample_package_details(request):
    try:
        # Get all tour packages
        packages = TourPackage.objects.all()
        
        for package in packages:
            # Add sample FAQs
            faqs = [
                {
                    'question': 'What is the best time to visit?',
                    'answer': f'The best time to visit {package.location} depends on your preferences. Generally, the peak season offers the best weather conditions but might be more crowded and expensive.'
                },
                {
                    'question': 'Is travel insurance included?',
                    'answer': 'Yes, basic travel insurance is included in the package. However, we recommend getting additional coverage for complete peace of mind.'
                },
                {
                    'question': 'What is the cancellation policy?',
                    'answer': 'Free cancellation up to 7 days before departure. Cancellations within 7 days will incur charges based on our policy.'
                },
                {
                    'question': 'Are meals included?',
                    'answer': 'Daily breakfast and dinner are included. Lunch and beverages are not included unless specifically mentioned in the itinerary.'
                }
            ]
            
            for faq_data in faqs:
                FAQ.objects.get_or_create(
                    tour_package=package,
                    question=faq_data['question'],
                    answer=faq_data['answer']
                )
            
            # Add sample reviews
            reviews = [
                {
                    'rating': 5,
                    'comment': f'Amazing experience in {package.location}! The tour was well-organized and the guide was very knowledgeable.',
                    'reviewer_name': 'John Smith'
                },
                {
                    'rating': 4,
                    'comment': 'Great tour package with good accommodation and services. Could improve on the food options.',
                    'reviewer_name': 'Emma Wilson'
                },
                {
                    'rating': 5,
                    'comment': 'Excellent value for money. Will definitely book again!',
                    'reviewer_name': 'Michael Brown'
                }
            ]
            
            for review_data in reviews:
                Review.objects.get_or_create(
                    tour_package=package,
                    rating=review_data['rating'],
                    comment=review_data['comment'],
                    reviewer_name=review_data['reviewer_name']
                )
            
            # Add detailed itinerary for remaining days
            for day in range(3, package.duration + 1):
                Itinerary.objects.get_or_create(
                    tour_package=package,
                    day_number=day,
                    title=f"Day {day} Activities",
                    description=f"""
                    Morning: Breakfast at hotel
                    Sightseeing and activities based on location
                    Afternoon: Free time for shopping/relaxation
                    Evening: Cultural program or leisure activities
                    Dinner at hotel
                    """
                )
        
        messages.success(request, "Sample package details (FAQs, Reviews, Itineraries) added successfully!")
        return redirect('packages')
        
    except Exception as e:
        messages.error(request, f"Error adding sample package details: {str(e)}")
        return redirect('packages')

@login_required
def payment_receipt(request, booking_id):
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        payment = booking.payments.first()

        if not payment:
            messages.error(request, 'No payment found for this booking')
            return redirect('my_bookings')

        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph('Payment Receipt', title_style))
        elements.append(Spacer(1, 20))

        # Customer Details
        elements.append(Paragraph('Customer Details', styles['Heading2']))
        current_date = timezone.now().strftime('%B %d, %Y')
        
        # Get lead passenger if available
        lead_passenger = booking.passenger.first() if hasattr(booking, 'passenger') else None
        
        customer_data = [
            ['Name', booking.user.username],
            ['Email', booking.user.email],
            ['Date', current_date],
            ['Transaction ID', str(payment.id)]
        ]
        
        # Add lead passenger info if available
        if lead_passenger:
            customer_data.append(['Lead Passenger', lead_passenger.name])
            customer_data.append(['Total Passengers', str(booking.passenger.count())])
        
        customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 20))

        # Calculate taxes
        tax_breakdown = calculate_taxes(booking)

        # Payment Details
        elements.append(Paragraph('Payment Details', styles['Heading2']))
        payment_data = [
            ['Description', 'Amount'],
            ['Package Cost', f'₹{booking.tour_package.price:,.2f}'],
            ['Flight Cost', f'₹{booking.flight.price:,.2f}'],
            ['Subtotal', f'₹{tax_breakdown["subtotal"]:,.2f}'],
            ['Package GST (18%)', f'₹{tax_breakdown["package_gst"]:,.2f}'],
            ['Flight GST (18%)', f'₹{tax_breakdown["flight_gst"]:,.2f}'],
            ['Service Charge (5%)', f'₹{tax_breakdown["service_charge"]:,.2f}'],
            ['Convenience Fee', f'₹{tax_breakdown["convenience_fee"]:,.2f}'],
            ['Total Amount', f'₹{payment.amount:,.2f}']
        ]
        payment_table = Table(payment_data, colWidths=[3*inch, 3*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 30))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            textColor=colors.HexColor('#6c757d'),
            fontSize=8,
            alignment=1
        )
        elements.append(Paragraph('This is a computer-generated document. No signature is required.', footer_style))
        elements.append(Paragraph('Thank you for choosing TravelXpert!', footer_style))

        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        # Generate response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{booking.id}.pdf"'
        response.write(pdf)

        return response

    except Exception as e:
        messages.error(request, f'Error generating bill: {str(e)}')
        return redirect('my_bookings')

def calculate_taxes(booking):
    # Convert percentages to Decimal
    GST_RATE = Decimal('0.18')  # 18%
    SERVICE_CHARGE_RATE = Decimal('0.05')  # 5%
    CONVENIENCE_FEE = Decimal('500')  # Fixed fee
    
    # Calculate GST (18% of base price)
    package_gst = booking.tour_package.price * GST_RATE
    flight_gst = booking.flight.price * GST_RATE
    
    # Calculate service charge (5% of base price)
    service_charge = (booking.tour_package.price + booking.flight.price) * SERVICE_CHARGE_RATE
    
    total_taxes = package_gst + flight_gst + service_charge + CONVENIENCE_FEE
    
    subtotal = booking.tour_package.price + booking.flight.price
    
    return {
        'package_gst': round(package_gst, 2),
        'flight_gst': round(flight_gst, 2),
        'service_charge': round(service_charge, 2),
        'convenience_fee': CONVENIENCE_FEE,
        'total_taxes': round(total_taxes, 2),
        'subtotal': round(subtotal, 2)
    }

@login_required
def view_bill(request, booking_id, payment_id):
    try:
        # Get booking and payment objects
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        payment = get_object_or_404(Payment, id=payment_id, booking=booking)
        
        # Calculate taxes
        tax_breakdown = calculate_taxes(booking)
        
        context = {
            'booking': booking,
            'payment': payment,
            'tax_breakdown': tax_breakdown,
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        }
        return render(request, 'bill.html', context)
        
    except Exception as e:
        messages.error(request, f'Error viewing bill: {str(e)}')
        return redirect('my_bookings')

def test_email(request):
    try:
        subject = 'Test Email'
        message = 'This is a test email from TravelXpert'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['mkambika287@gmail.com']
        
        email = EmailMultiAlternatives(
            subject,
            message,
            from_email,
            recipient_list
        )
        
        email.send(fail_silently=False)
        return HttpResponse('Test email sent successfully!')
    except Exception as e:
        return HttpResponse(f'Error sending email: {str(e)}')
    

from django.db.models import Q
from .models import TourPackage

def search_tours(request):
    tours = TourPackage.objects.all()
    categories = TourPackage.objects.values_list('category', flat=True).distinct()
    
    # Get filter parameters
    search_query = request.GET.get('search_query', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    # Apply filters based on which parameter is present
    if search_query:
        tours = tours.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    elif category:
        tours = tours.filter(category=category)
    elif min_price or max_price:
        if min_price:
            tours = tours.filter(price__gte=min_price)
        if max_price:
            tours = tours.filter(price__lte=max_price)
    
    context = {
        'tours': tours,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'selected_min_price': min_price,
        'selected_max_price': max_price
    }
    
    return render(request, 'search_results.html', context)

@login_required
def diary_list(request):
    if request.user.is_authenticated:
        # Get user's own diaries and public diaries from other users
        user_diaries = TravelDiary.objects.filter(user=request.user)
        public_diaries = TravelDiary.objects.filter(visibility='public').exclude(user=request.user)
        diaries = user_diaries | public_diaries
        diaries = diaries.order_by('-created_at')
        return render(request, 'diary_list.html', {'diaries': diaries})
    return redirect('login')

@login_required
def create_diary(request):
    if request.method == 'POST':
        diary_form = TravelDiaryForm(request.POST)
        image_form = DiaryImageForm()
        
        if diary_form.is_valid():
            diary = diary_form.save(commit=False)
            diary.user = request.user
            diary.save()
            
            # Handle image uploads
            images = request.FILES.getlist('image')
            for img in images:
                DiaryImage.objects.create(
                    diary=diary,
                    image=img,
                    caption=request.POST.get('caption', '')
                )
            
            messages.success(request, 'Travel diary created successfully!')
            return redirect('diary_detail', pk=diary.pk)
    else:
        diary_form = TravelDiaryForm()
        image_form = DiaryImageForm()
    
    return render(request, 'create_diary.html', {
        'diary_form': diary_form,
        'image_form': image_form
    })

@login_required
def diary_detail(request, pk):
    diary = get_object_or_404(TravelDiary, pk=pk)
    # Check if the user has permission to view this diary
    if diary.visibility == 'private' and diary.user != request.user:
        messages.error(request, 'You do not have permission to view this diary.')
        return redirect('diary_list')
    return render(request, 'diary_detail.html', {'diary': diary})

@login_required
def edit_diary(request, pk):
    diary = get_object_or_404(TravelDiary, pk=pk)
    
    # Check if the logged-in user is the owner of the diary
    if diary.user != request.user:
        messages.error(request, 'You do not have permission to edit this diary.')
        return redirect('diary_list')
    
    if request.method == 'POST':
        diary_form = TravelDiaryForm(request.POST, instance=diary)
        image_form = DiaryImageForm(request.POST, request.FILES)
        
        if diary_form.is_valid():
            # Save the diary form
            diary = diary_form.save(commit=False)
            diary.save()
            
            # Handle image upload
            if image_form.is_valid() and 'image' in request.FILES:
                new_image = image_form.save(commit=False)
                new_image.diary = diary
                new_image.save()
            
            messages.success(request, 'Travel diary updated successfully!')
            return redirect('diary_detail', pk=diary.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        diary_form = TravelDiaryForm(instance=diary)
        image_form = DiaryImageForm()
    
    return render(request, 'edit_diary.html', {
        'diary_form': diary_form,
        'image_form': image_form,
        'diary': diary
    })

@login_required
def delete_diary(request, pk):
    diary = get_object_or_404(TravelDiary, pk=pk)
    
    # Check if the logged-in user is the owner of the diary
    if diary.user != request.user:
        messages.error(request, 'You do not have permission to delete this diary.')
        return redirect('diary_list')
    
    if request.method == 'POST':
        # Delete all associated images first
        diary.images.all().delete()
        # Delete the diary
        diary.delete()
        messages.success(request, 'Travel diary deleted successfully!')
        return redirect('diary_list')
    
    # For GET request, show confirmation page
    return render(request, 'delete_diary.html', {
        'diary': diary,
        'image_count': diary.images.count()
    })

@login_required
def delete_diary_image(request, image_pk):
    image = get_object_or_404(DiaryImage, pk=image_pk)
    
    if image.diary.user != request.user:
        messages.error(request, 'You do not have permission to delete this image.')
        return redirect('diary_detail', pk=image.diary.pk)
    
    if request.method == 'POST':
        diary_pk = image.diary.pk
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('diary_detail', pk=diary_pk)
    
    return render(request, 'delete_diary_image.html', {'image': image})

@login_required
def edit_image_caption(request, pk, image_pk):
    diary = get_object_or_404(TravelDiary, pk=pk)
    image = get_object_or_404(DiaryImage, pk=image_pk, diary=diary)
    
    if diary.user != request.user:
        messages.error(request, 'You do not have permission to edit this image.')
        return redirect('diary_detail', pk=diary.pk)
    
    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        image.caption = caption
        image.save()
        messages.success(request, 'Image caption updated successfully!')
    
    return redirect('diary_detail', pk=diary.pk)

@login_required
def delete_diary_image(request, pk, image_pk):
    diary = get_object_or_404(TravelDiary, pk=pk)
    image = get_object_or_404(DiaryImage, pk=image_pk, diary=diary)
    
    if diary.user != request.user:
        messages.error(request, 'You do not have permission to delete this image.')
        return redirect('diary_detail', pk=diary.pk)
    
    image.delete()
    messages.success(request, 'Image deleted successfully!')
    return redirect('diary_detail', pk=diary.pk)

# ______________________________________________________________________________________________________________


from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FlightBooking, PackingPreferences, PackingList

@login_required
def view_packing_list(request, booking_id):
    """View the packing list for a booking."""
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        preferences = get_object_or_404(PackingPreferences, booking=booking)
        
        # Check if we need to generate a new list
        packing_list = PackingList.objects.filter(booking=booking).first()
        if not packing_list or not preferences.last_generated:
            # Generate new list using Gemini
            try:
                result = generate_packing_list(
                    trip_types=preferences.trip_categories,
                    weather=preferences.weather,
                    traveling_with_kids=preferences.traveling_with_kids,
                    special_requirements=preferences.special_requirements
                )
                
                # Create new packing list
                packing_list = PackingList.objects.create(
                    booking=booking,
                    preferences=preferences,
                    source=result.get('source', 'default')
                )
                
                # Save items by category
                for category, items in result.get('categories', {}).items():
                    for item in items:
                        if item:  # Skip None values
                            PackingItem.objects.create(
                                packing_list=packing_list,
                                category=category,
                                name=item
                            )
                
                # Update last generated timestamp
                preferences.last_generated = timezone.now()
                preferences.save()
                
            except Exception as e:
                messages.error(request, f"Error generating packing list: {str(e)}")
                if not packing_list:
                    # Create default items if we have nothing
                    packing_list = PackingList.objects.create(
                        booking=booking,
                        preferences=preferences,
                        source='default'
                    )
                    packing_list.items = {
                        'essential_documents': [
                            'Passport/ID',
                            'Travel insurance',
                            'Booking confirmations',
                            'Emergency contacts'
                        ],
                        'clothing': [
                            'Weather-appropriate clothing',
                            'Comfortable shoes',
                            'Sleepwear'
                        ],
                        'toiletries': [
                            'Toothbrush & toothpaste',
                            'Shampoo & conditioner',
                            'Personal care items'
                        ],
                        'electronics': [
                            'Phone & charger',
                            'Camera',
                            'Power bank'
                        ]
                    }
                    packing_list.save()
        
        # Get items grouped by category
        items_by_category = {}
        for item in PackingItem.objects.filter(packing_list=packing_list):
            if item.category not in items_by_category:
                items_by_category[item.category] = []
            items_by_category[item.category].append(item.name)
        
        return render(request, 'packing_list.html', {
            'booking': booking,
            'preferences': preferences,
            'selected_items': items_by_category,
            'is_ai_generated': packing_list.source == 'gemini'
        })
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('my_bookings')
    

from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FlightBooking, PackingPreferences

@login_required
def packing_preferences(request, booking_id):
    """Handle packing preferences form."""
    try:
        booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
        
        # Get or create preferences
        preferences, created = PackingPreferences.objects.get_or_create(
            booking=booking,
            defaults={
                'trip_categories': ['general'],
                'weather': 'moderate',
                'traveling_with_kids': False
            }
        )
        
        if request.method == 'POST':
            # Get form data
            trip_types = request.POST.getlist('trip_types')
            weather = request.POST.get('weather', 'moderate')
            traveling_with_kids = request.POST.get('traveling_with_kids') == 'on'
            special_requirements = request.POST.get('special_requirements', '')
            
            # Validate trip types
            if not trip_types:
                trip_types = ['general']
            
            # Update preferences
            preferences.trip_categories = trip_types
            preferences.weather = weather
            preferences.traveling_with_kids = traveling_with_kids
            preferences.special_requirements = special_requirements
            preferences.last_generated = None  # Force regeneration of packing list
            preferences.save()
            
            # Delete existing packing list to force regeneration
            PackingList.objects.filter(booking=booking).delete()
            
            messages.success(request, "Packing preferences updated successfully!")
            return redirect('view_packing_list', booking_id=booking_id)
        
        return render(request, 'packing_preferences.html', {
            'booking': booking,
            'preferences': preferences
        })
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('my_bookings')

import requests
from datetime import datetime
import json

def get_weather(request, destination):
    try:
        # OpenWeatherMap API endpoint
        api_key = "f229289322fdc62ee4f1b9cc6d067445"
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        # Clean up destination
        original_location = destination
        cities = [c.strip() for c in destination.replace('-', ',').replace('/', ',').split(',')]
        city = cities[0]  # Take the first city
        
        # Special city-country mappings
        city_country_mapping = {
            'dubai': 'Dubai,AE',
            'delhi': 'New Delhi,IN',
            'new delhi': 'New Delhi,IN',
            'mumbai': 'Mumbai,IN',
            'kolkata': 'Kolkata,IN',
            'bangalore': 'Bengaluru,IN',
            'chennai': 'Chennai,IN',
            'paris': 'Paris,FR',
            'london': 'London,GB',
            'new york': 'New York,US',
            'tokyo': 'Tokyo,JP',
            'singapore': 'Singapore,SG',
            'rishikesh': 'Rishikesh,IN'
        }
        
        # Clean city name and check mapping
        city_lower = city.lower()
        search_query = city_country_mapping.get(city_lower, f"{city},IN")  # Default to India if not in mapping
        
        # Make API request
        params = {
            'q': search_query,
            'appid': api_key,
            'units': 'metric'  # Get temperature in Celsius
        }
        
        response = requests.get(base_url, params=params, timeout=10)  # Add timeout
        
        context = {
            'location': original_location,
            'primary_city': city
        }
        
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                'temp': round(data['main']['temp'], 1),
                'temp_min': round(data['main']['temp_min'], 1),
                'temp_max': round(data['main']['temp_max'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'], 1),
                'pressure': data['main']['pressure'],
                'city': data['name'],
                'country': data['sys']['country'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p'),
                'timezone': data['timezone'],
                'visibility': data.get('visibility', 0) / 1000,  # Convert to kilometers
                'clouds': data['clouds']['all']
            }
            
            # Check for severe weather conditions
            alerts = check_severe_weather(weather_data)
            if alerts and request.user.is_authenticated:
                send_weather_alert(
                    request.user.email,
                    request.user.username,
                    weather_data['city'],
                    weather_data,
                    alerts
                )
                context['weather_alerts'] = alerts
            
            context['weather'] = weather_data
            context['error'] = None
        else:
            error_data = response.json() if response.content else {'message': 'Unknown error'}
            error_message = error_data.get('message', 'Could not fetch weather data')
            context['error'] = f"Could not fetch weather data for {city}. {error_message}"
            
        return render(request, 'weather_info.html', context)
            
    except requests.RequestException as e:
        print(f"Weather API Error: {str(e)}")
        return render(request, 'weather_info.html', {
            'location': destination,
            'error': 'Error connecting to weather service. Please check your internet connection and try again.',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        })
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return render(request, 'weather_info.html', {
            'location': destination,
            'error': 'An unexpected error occurred. Please try again later.',
            'user_profile': request.user.userprofile if hasattr(request.user, 'userprofile') else None
        })

def check_severe_weather(weather_data):
    """Check if weather conditions are severe."""
    alerts = []
    
    # Temperature alerts
    if weather_data['temp'] > 35:
        alerts.append('Extreme heat conditions')
    elif weather_data['temp'] < 0:
        alerts.append('Freezing conditions')
        
    # Wind alerts
    if weather_data['wind_speed'] > 10:
        alerts.append('Strong winds')
        
    # Visibility alerts
    if weather_data.get('visibility', 10) < 5:
        alerts.append('Poor visibility')
        
    # Humidity alerts
    if weather_data['humidity'] > 85:
        alerts.append('Very high humidity')
        
    return alerts

def send_weather_alert(user_email, user_name, destination, weather_data, alerts):
    """Send weather alert email to user."""
    try:
        weather_url = f"/weather/{destination}/"  # URL to weather details page
        
        # Prepare email context
        context = {
            'user_name': user_name,
            'destination': destination,
            'weather': weather_data,
            'weather_url': weather_url,
            'alerts': alerts
        }
        
        # Render email template
        html_content = render_to_string('emails/weather_alert_email.html', context)
        text_content = strip_tags(html_content)
        
        # Create email subject
        alert_types = ', '.join(alerts)
        subject = f'Weather Alert: {alert_types} in {destination}'
        
        # Send email
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        print(f"Weather alert email sent to {user_email}")
        return True
    except Exception as e:
        print(f"Error sending weather alert email: {str(e)}")
        return False

def weather_check(request):
    """Handle weather check form submission."""
    if request.method == 'GET':
        city = request.GET.get('city')
        if city:
            # Redirect to the weather detail page for the city
            return redirect('weather_detail', destination=city)
        else:
            # If no city provided, show popular destinations
            popular_cities = [
                {'name': 'Dubai', 'country': 'UAE', 'image': 'dubai.jpg'},
                {'name': 'Singapore', 'country': 'Singapore', 'image': 'singapore.jpg'},
                {'name': 'Paris', 'country': 'France', 'image': 'paris.jpg'},
                {'name': 'London', 'country': 'UK', 'image': 'london.jpg'},
                {'name': 'New York', 'country': 'USA', 'image': 'newyork.jpg'},
                {'name': 'Tokyo', 'country': 'Japan', 'image': 'tokyo.jpg'},
            ]
            return render(request, 'weather_check.html', {'cities': popular_cities})
    
    # If not GET, redirect to home
    return redirect('home')

@login_required
def add_packing_item(request, booking_id):
    """Add a custom item to the packing list."""
    if request.method == 'POST':
        try:
            booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
            packing_list = get_object_or_404(PackingList, booking=booking)
            
            item = request.POST.get('item')
            category = request.POST.get('category', 'custom')
            
            if not item:
                messages.error(request, "Please provide an item to add.")
                return redirect('view_packing_list', booking_id=booking_id)
            
            # Initialize the category if it doesn't exist
            if category not in packing_list.items:
                packing_list.items[category] = []
                
            # Add the item if it's not already in the list
            if item not in packing_list.items[category]:
                packing_list.items[category].append(item)
                packing_list.save()
                messages.success(request, f"Added '{item}' to your packing list.")
            else:
                messages.info(request, f"'{item}' is already in your packing list.")
                
        except Exception as e:
            messages.error(request, f"Error adding item to packing list: {str(e)}")
            
    return redirect('view_packing_list', booking_id=booking_id)

@login_required
def edit_packing_item(request, booking_id, pk):
    """Edit an existing item in the packing list."""
    if request.method == 'POST':
        try:
            booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
            packing_list = get_object_or_404(PackingList, booking=booking)
            
            old_item = request.POST.get('old_item')
            new_item = request.POST.get('new_item')
            old_category = request.POST.get('old_category')
            new_category = request.POST.get('new_category', old_category)
            
            if not new_item:
                messages.error(request, "Please provide a new item name.")
                return redirect('view_packing_list', booking_id=booking_id)
            
            # Remove item from old category
            if old_category in packing_list.items and old_item in packing_list.items[old_category]:
                packing_list.items[old_category].remove(old_item)
                
                # Remove category if empty
                if not packing_list.items[old_category]:
                    del packing_list.items[old_category]
            
            # Add item to new category
            if new_category not in packing_list.items:
                packing_list.items[new_category] = []
            
            # Add new item if it doesn't already exist
            if new_item not in packing_list.items[new_category]:
                packing_list.items[new_category].append(new_item)
                packing_list.save()
                messages.success(request, f"Updated packing list item from '{old_item}' to '{new_item}'")
            else:
                messages.info(request, f"'{new_item}' is already in your packing list under {new_category}")
                
        except Exception as e:
            messages.error(request, f"Error updating packing list item: {str(e)}")
            
    return redirect('view_packing_list', booking_id=booking_id)

@login_required
def delete_packing_item(request, booking_id, pk):
    """Delete an item from the packing list."""
    if request.method == 'POST':
        try:
            booking = get_object_or_404(FlightBooking, id=booking_id, user=request.user)
            packing_list = get_object_or_404(PackingList, booking=booking)
            
            item = request.POST.get('item')
            category = request.POST.get('category')
            
            if not item or not category:
                messages.error(request, "Please provide both item and category to delete.")
                return redirect('view_packing_list', booking_id=booking_id)
            
            # Remove item from category
            if category in packing_list.items and item in packing_list.items[category]:
                packing_list.items[category].remove(item)
                
                # Remove category if empty
                if not packing_list.items[category]:
                    del packing_list.items[category]
                    
                packing_list.save()
                messages.success(request, f"Removed '{item}' from your packing list.")
            else:
                messages.info(request, f"Item '{item}' was not found in category '{category}'.")
                
        except Exception as e:
            messages.error(request, f"Error deleting packing list item: {str(e)}")
            
    return redirect('view_packing_list', booking_id=booking_id)

from django.shortcuts import render, redirect
from .models import (
    FlightBooking, 
    PackingPreferences,
    PackingList,
    PackingItem,
    TravelDiary,
    DiaryImage,
    Review,
    UserProfile,
    TourPackage,
    Flight,
    Itinerary,
    InclusionsExclusions,
    Passenger,
    Payment,
    LandmarkDetection
)
from .forms import (
    PassengerForm, 
    TourPackageForm, 
    TourPackageUpdateForm, 
    FlightBookingForm, 
    PaymentForm, 
    LandmarkUploadForm, 
    TravelDiaryForm, 
    DiaryImageForm
)
from .utils.gemini_api import generate_packing_list


import os
import google.generativeai as genai
from django.shortcuts import render, redirect
from .models import LandmarkDetection
from .forms import LandmarkImageForm
from django.contrib.auth.decorators import login_required

# Configure Google Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Set up Gemini model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=generation_config)
from PIL import Image
import io
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LandmarkDetection
from .forms import LandmarkImageForm

def detect_landmark(image_path):
    """ Sends the image to Google Gemini for detailed landmark detection """

    with open(image_path, "rb") as img_file:
        image_data = img_file.read()  # Read image in binary mode

    # Convert image data to PIL Image
    image = Image.open(io.BytesIO(image_data))

    # Start a chat session and send the image with an expanded query
    chat_session = model.start_chat(history=[
        {"role": "user", "parts": [
            "Identify the landmark in this image and provide the following details:"
            "\n1. Name and Location"
            "\n2. Historical Background"
            "\n   - Year of Construction"
            "\n   - Original Builders or Architects"
            "\n   - Major Historical Events Associated with It"
            "\n   - UNESCO World Heritage Status (if applicable)"
            "\n   - Restoration and Preservation Efforts"
            "\n   - Notable Personalities Linked to This Landmark"
            "\n3. Architectural Features"
            "\n4. Cultural and Spiritual Significance"
            "\n5. Events and Festivals Held Here"
            "\n6. Visitor Information (Best Time, Entry Fee, etc.)"
            "\n7. Nearby Attractions"
            "\n8. Interesting Facts"
            "\n9. Legends or Myths Associated with It"
            "\n10. Current Use and Accessibility Status"
        ]}
    ])
    
    response = chat_session.send_message(image)  # Send the PIL image

    return response.text if response else "Could not identify the landmark."

@login_required
def upload_image(request):
    """ Handle image uploads, store results, and associate with the user """
    if request.method == 'POST':
        form = LandmarkImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.user = request.user  # Associate with logged-in user
            image_instance.save()

            # Detect landmark with detailed information
            landmark_info = detect_landmark(image_instance.image.path)
            landmark_info = landmark_info.replace("*", "")  # Remove unwanted asterisks

            image_instance.detected_landmark = landmark_info
            image_instance.save()

            return render(request, 'result.html', {'image': image_instance.image.url, 'info': landmark_info})
    else:
        form = LandmarkImageForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def history(request):
    """ Show the user's past landmark detections """
    detections = LandmarkDetection.objects.filter(user=request.user).order_by('-detection_date')
    return render(request, 'history.html', {'detections': detections})




import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from .models import SummarizationRequest
from .forms import SummarizerForm

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
)

def summarize_text(text):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(text)
    
    print("API Response:", response)  # Debugging
    
    if hasattr(response, 'text'):
        return response.text
    else:
        return f"Error: Unexpected API response {response}"

def summarize_view(request):
    if request.method == "POST":
        form = SummarizerForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data["input_text"]
            print("Input received:", input_text)
            summary = summarize_text(input_text)
            print("Generated summary:", summary)
            return JsonResponse({"summary": summary})
    return JsonResponse({"error": "Invalid request"}, status=400)




import os
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Load API Key securely
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "AIzaSyC1yEZXp9L024y2OjldPLVq-RkTYZRebeU")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'reply': "Please enter a message."})

        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {"role": "user", "parts": [{"text": user_message}]}
            ]
        }

        try:
            response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=data)
            response.raise_for_status()
            api_response = response.json()
            candidates = api_response.get("candidates", [])

            if candidates:
                bot_reply = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "I couldn't process that.")
                bot_reply = bot_reply.split(".")[0] + "."  # Keep only the first sentence
            else:
                bot_reply = "I'm not sure. Can you ask differently?"

        except requests.exceptions.RequestException:
            bot_reply = "Sorry, I can't process your request now."

        return JsonResponse({'reply': bot_reply})

    return render(request, 'chatbot.html')




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review, FlightBooking
from .forms import ReviewForm

@login_required
def review_list(request):
    """Display all reviews."""
    reviews = Review.objects.all()
    return render(request, 'review_list.html', {'reviews': reviews})

@login_required
def add_review(request, booking_id):
    """Allow a user to add a review for a specific booking."""
    booking = get_object_or_404(FlightBooking, id=booking_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            return redirect('review_list')  # Redirect to reviews page
    else:
        form = ReviewForm()

    return render(request, 'review_form.html', {'form': form, 'booking': booking})

@login_required
def review_detail(request, review_id):
    """View a specific review."""
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'review_detail.html', {'review': review})

@login_required
def delete_review(request, review_id):
    """Delete a review (only for the review owner)."""
    review = get_object_or_404(Review, id=review_id)

    if request.user == review.booking.user:  # Ensure only the owner can delete
        review.delete()
        return redirect('review_list')
    else:
        return redirect('review_detail', review_id=review.id)
    

    
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64
from django.shortcuts import render
# Function to create a base64 image from a figure
def get_base64_chart(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    encoded_chart = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f"data:image/png;base64,{encoded_chart}"

def admin_reports(request):
    # 1. Tour Packages by Category
    categories = TourPackage.objects.values_list('category', flat=True)
    category_counts = pd.Series(categories).value_counts()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    category_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Set3', ax=ax1)
    plt.title("Tour Packages by Category")
    plt.ylabel('')
    tour_category_chart = get_base64_chart(fig1)

    # 2. Flight Booking Status
    statuses = FlightBooking.objects.values_list('booking_status', flat=True)
    status_counts = pd.Series(statuses).value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    status_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='coolwarm', ax=ax2)
    plt.title("Flight Booking Status")
    plt.ylabel('')
    flight_status_chart = get_base64_chart(fig2)

    # 3. Payment Methods Distribution
    methods = Payment.objects.values_list('payment_method', flat=True)
    method_counts = pd.Series(methods).value_counts()
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    method_counts.plot(kind='bar', color='teal', ax=ax3)
    plt.xlabel("Payment Method")
    plt.ylabel("Count")
    plt.title("Revenue from Payment Methods")
    plt.xticks(rotation=45)
    payment_method_chart = get_base64_chart(fig3)

    # 4. Average Rating of Tour Packages
    ratings = Review.objects.values_list('rating', flat=True)
    rating_counts = pd.Series(ratings).value_counts().sort_index()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="Blues_r", ax=ax4)
    plt.xlabel("Rating")
    plt.ylabel("Number of Reviews")
    plt.title("Average Tour Package Rating")
    avg_rating_chart = get_base64_chart(fig4)

    # Send all charts to the template
    context = {
        'tour_category_chart': tour_category_chart,
        'flight_status_chart': flight_status_chart,
        'payment_method_chart': payment_method_chart,
        'avg_rating_chart': avg_rating_chart,
    }
    return render(request, 'admin_reports.html', context)
