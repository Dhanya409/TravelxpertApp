# Generated by Django 5.1.5 on 2025-01-20 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tourpackage',
            name='category',
            field=models.CharField(choices=[('domestic', 'Domestic Tours'), ('international', 'International Tours'), ('adventure', 'Adventure Tours'), ('romantic', 'Romantic Getaways'), ('family', 'Family Holidays'), ('wellness', 'Wellness Retreats'), ('budget', 'Budget-Friendly'), ('mid_range', 'Mid-Range'), ('luxury', 'Luxury Packages')], default='domestic', max_length=20),
        ),
    ]
