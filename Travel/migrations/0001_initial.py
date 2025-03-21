# Generated by Django 4.2.5 on 2024-12-30 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=20)),
                ('airline', models.CharField(max_length=100)),
                ('departure_city', models.CharField(max_length=100)),
                ('arrival_city', models.CharField(max_length=100)),
                ('departure_date', models.DateField()),
                ('departure_time', models.TimeField()),
                ('arrival_date', models.DateField()),
                ('arrival_time', models.TimeField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_seats', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FlightBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('booking_status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('seat_class', models.CharField(choices=[('economy', 'Economy'), ('business', 'Business'), ('first', 'First Class')], default='economy', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cancellation_reason', models.TextField(blank=True, null=True)),
                ('cancellation_date', models.DateTimeField(blank=True, null=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Travel.flight')),
            ],
            options={
                'ordering': ['-booking_date'],
            },
        ),
        migrations.CreateModel(
            name='TourPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_slots', models.IntegerField()),
                ('duration', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('image', models.ImageField(upload_to='tour_images/')),
                ('location', models.CharField(max_length=255)),
                ('highlights', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('review_text', models.TextField()),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Travel.flightbooking')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('refund_date', models.DateTimeField(auto_now_add=True)),
                ('processed_date', models.DateTimeField(blank=True, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Travel.flightbooking')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('upi', 'UPI'), ('net_banking', 'Net Banking')], max_length=20)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payment_details', models.JSONField(default=dict)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='Travel.flightbooking')),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('age', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LandmarkDetection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='landmarks/')),
                ('detected_landmark', models.CharField(blank=True, max_length=255, null=True)),
                ('detection_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.IntegerField(default=1)),
                ('title', models.CharField(default='Day Activity', max_length=200)),
                ('description', models.TextField(default='Details will be provided')),
                ('location', models.CharField(default='To be announced', max_length=200)),
                ('duration', models.CharField(default='Full Day', max_length=50)),
                ('meals', models.CharField(default='Breakfast', max_length=100)),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itineraries', to='Travel.tourpackage')),
            ],
            options={
                'ordering': ['day_number'],
            },
        ),
        migrations.CreateModel(
            name='InclusionsExclusions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inclusions', models.TextField(help_text='List all inclusions for this package')),
                ('exclusions', models.TextField(help_text='List all exclusions for this package')),
                ('tour_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inclusions_exclusions', to='Travel.tourpackage')),
            ],
        ),
        migrations.AddField(
            model_name='flightbooking',
            name='passenger',
            field=models.ManyToManyField(to='Travel.passenger'),
        ),
        migrations.AddField(
            model_name='flightbooking',
            name='tour_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Travel.tourpackage'),
        ),
        migrations.AddField(
            model_name='flightbooking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=12, null=True)),
                ('password', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
