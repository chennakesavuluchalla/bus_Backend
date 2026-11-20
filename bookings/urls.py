from django.urls import path
# 1. Add UserProfileView to the imports here
from .views import (
    RegisterView, 
    LoginView, 
    BusListCreateView, 
    BusDetailView, 
    UserBookingView, 
    BookingView,
    UserProfileView,
    CancelBookingView,  # <--- ADDED THIS
)

urlpatterns = [
    path('buses/', BusListCreateView.as_view(), name='buslist'),
    path('buses/<int:pk>/', BusDetailView.as_view(), name='bus-detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/bookings', UserBookingView.as_view(), name='user_bookings'),
    path('booking/', BookingView.as_view(), name='bookings'),
    path('booking/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='cancel_booking'), 

    
    # 2. Remove "api/" from the start and use the imported class directly
    path('user/<int:user_id>', UserProfileView.as_view()), # <--- FIXED THIS
]

