# Generated by Django 5.1.5 on 2025-02-17 03:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Travel', '0008_passportdetails_traveldiary_diaryimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.JSONField(default=dict, null=True)),
                ('source', models.CharField(choices=[('gemini', 'AI Generated'), ('default', 'Default List')], default='default', max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packing_list', to='Travel.flightbooking')),
            ],
        ),
        migrations.CreateModel(
            name='PackingItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('packing_list', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packing_items', to='Travel.packinglist')),
            ],
        ),
        migrations.CreateModel(
            name='PackingPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_categories', models.JSONField(default=list, null=True)),
                ('weather', models.CharField(choices=[('hot', 'Hot'), ('moderate', 'Moderate'), ('cold', 'Cold'), ('rainy', 'Rainy')], default='moderate', max_length=20, null=True)),
                ('traveling_with_kids', models.BooleanField(default=False, null=True)),
                ('special_requirements', models.TextField(blank=True, null=True)),
                ('last_generated', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packing_preferences', to='Travel.flightbooking')),
            ],
        ),
        migrations.AddField(
            model_name='packinglist',
            name='preferences',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='packing_list', to='Travel.packingpreferences'),
        ),
    ]
