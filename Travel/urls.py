from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import messages

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('destination/', views.destination, name='destination'),
    path('hotel/', views.hotel, name='hotel'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('packages/', views.tour_packages, name='packages'),
    path('packages/<str:category>/', views.packages_by_category, name='packages_by_category'),
    path('add/', views.tour_package_add, name='tour_package_add'),
    path('<int:pk>/update/', views.tour_package_update, name='tour_package_update'),
    path('<int:pk>/delete/', views.tour_package_delete, name='tour_package_delete'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('package/<int:package_id>/itinerary/', views.itinerary_overview, name='itinerary_overview'),
    path('package/<int:package_id>/service/', views.package_service, name='package_service'),
    path('package/<int:package_id>/select-flight/', views.select_flight, name='select_flight'),
    path('process_booking/<int:flight_id>/<int:package_id>/', views.process_booking, name='process_booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('process_payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('download-ticket/<int:booking_id>/', views.download_ticket, name='download_ticket'),
    path('download-bill/<int:booking_id>/', views.generate_bill, name='download_bill'),
    path('booking/itinerary/<int:booking_id>/', views.view_itinerary, name='view_itinerary'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('passenger-details/<int:package_id>/', views.passenger_details, name='passenger_details'),
    # User URLs
    path("dashboard/", views.dashboard, name="dashboard"),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    # Bill URLs
    path('bill/<int:booking_id>/<int:payment_id>/', views.view_bill, name='view_bill'),
    # Ticket and Bill Generation URLs
    path('booking/<int:booking_id>/generate-ticket/', views.generate_ticket, name='generate_ticket'),
    path('booking/<int:booking_id>/generate-bill/', views.generate_bill, name='generate_bill'),
    path('bill/<int:booking_id>/<int:payment_id>/', views.view_bill, name='view_bill'),
    path('download-receipt/<int:booking_id>/', views.download_receipt, name='download_receipt'),
    path('test-email/', views.test_email, name='test_email'),
    path('diaries/', views.diary_list, name='diary_list'),
    path('diary/create/', views.create_diary, name='create_diary'),
    path('diary/<int:pk>/', views.diary_detail, name='diary_detail'),
    path('diary/<int:pk>/edit/', views.edit_diary, name='edit_diary'),
    path('diary/<int:pk>/delete/', views.delete_diary, name='delete_diary'),
    path('diary/<int:pk>/image/<int:image_pk>/delete/', views.delete_diary_image, name='delete_diary_image'),
    path('diary/<int:pk>/image/<int:image_pk>/edit-caption/', views.edit_image_caption, name='edit_image_caption'),
    path('search/', views.search_tours, name='search_tours'),
    path('booking/<int:booking_id>/packing-preferences/', views.packing_preferences, name='packing_preferences'),
    path('booking/<int:booking_id>/packing-list/', views.view_packing_list, name='view_packing_list'),
    path('booking/<int:booking_id>/packing-list/add-item/', views.add_packing_item, name='add_packing_item'),
    path('booking/<int:booking_id>/packing-list/<int:pk>/edit/', views.edit_packing_item, name='edit_packing_item'),
    path('booking/<int:booking_id>/packing-list/<int:pk>/delete/', views.delete_packing_item, name='delete_packing_item'),
    # Weather URL
    path('weather/<str:destination>/', views.get_weather, name='get_weather'),
    path('upload/', views.upload_image, name='upload'),  
    path('result/', views.detect_landmark, name='result'),  
    path('history/', views.history, name='history'), 
    path("summarize/", views.summarize_view, name="summarize"),

    path('chat/', views.chat, name='chat'),


    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/<int:booking_id>/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    path('admin_reports/', views.admin_reports, name='admin_reports'),


]

# $env:GOOGLE_API_KEY="AIzaSyC1yEZXp9L024y2OjldPLVq-RkTYZRebeU"
