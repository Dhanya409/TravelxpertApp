# forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DiaryImage, FlightBooking, InclusionsExclusions, Itinerary, Passenger, Review, TourPackage, Payment, Customer, LandmarkDetection
from .models import TravelDiary


# Form to Add a New Tour Package
class TourPackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        fields = ['name', 'description', 'price', 'available_slots', 'duration', 'start_date', 'end_date', 'image', 'location', 'highlights']

# Form to Update an Existing Tour Package
class TourPackageUpdateForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        fields = ['name', 'description', 'price', 'available_slots', 'duration', 'start_date', 'end_date', 'image', 'location', 'highlights']

        
class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = ['day_number', 'title', 'description', 'location', 'duration', 'meals']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['full_name', 'email', 'phone', 'age']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your age'
            })
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number should only contain digits")
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError("Phone number should be between 10 and 15 digits")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 1:
            raise forms.ValidationError("Age must be greater than 0")
        if age > 120:
            raise forms.ValidationError("Please enter a valid age")
        return age


class InclusionsExclusionsForm(forms.ModelForm):
    class Meta:
        model = InclusionsExclusions
        fields = ['inclusions', 'exclusions']


class FlightBookingForm(forms.ModelForm):
    class Meta:
        model = FlightBooking
        fields = ['total_amount', 'booking_status']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'booking_status': forms.Select(attrs={'class': 'form-control'})
        }


class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(max_length=16, required=False)
    card_expiry = forms.CharField(max_length=5, required=False)
    card_cvv = forms.CharField(max_length=3, required=False)
    upi_id = forms.CharField(max_length=50, required=False)
    
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvv = cleaned_data.get('card_cvv')
            
            if not all([card_number, card_expiry, card_cvv]):
                raise forms.ValidationError('Card details are required for card payment')
        
        elif payment_method == 'upi':
            upi_id = cleaned_data.get('upi_id')
            if not upi_id:
                raise forms.ValidationError('UPI ID is required for UPI payment')
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CustomerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    phone = forms.CharField(max_length=12, required=False)

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError('Passwords do not match.')
            
            # Password strength validation
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            if not any(char.isupper() for char in password):
                raise forms.ValidationError('Password must contain at least one uppercase letter.')
            if not any(char.islower() for char in password):
                raise forms.ValidationError('Password must contain at least one lowercase letter.')
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError('Password must contain at least one number.')
            if not any(not char.isalnum() for char in password):
                raise forms.ValidationError('Password must contain at least one special character.')


class LandmarkUploadForm(forms.ModelForm):
    class Meta:
        model = LandmarkDetection
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this);'
            })
        }



class TravelDiaryForm(forms.ModelForm):
    class Meta:
        model = TravelDiary
        fields = ['title', 'content', 'location', 'travel_date', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter diary title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your travel experience'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}, choices=TravelDiary.VISIBILITY_CHOICES),
        }

class DiaryImageForm(forms.ModelForm):
    class Meta:
        model = DiaryImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a caption for your image'
            }),
        }

from django import forms
from .models import LandmarkDetection

class LandmarkImageForm(forms.ModelForm):
    class Meta:
        model = LandmarkDetection
        fields = ['image']


from django import forms

class SummarizerForm(forms.Form):
    input_text = forms.CharField(widget=forms.Textarea, label="Enter Text to Summarize")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
