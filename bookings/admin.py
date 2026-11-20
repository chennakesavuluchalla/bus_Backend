from django.contrib import admin
from .models import Bus, Seat, Booking

# Register your models here.

class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_name', 'bus_number', 'starting_at', 'destination')
    
class SeatAdmin(admin.ModelAdmin):
    # 🚨 REMOVED 'is_booked' from this list
    list_display = ('seat_number', 'bus')
    
class BookingAdmin(admin.ModelAdmin):
    # 🚨 ADDED 'travel_date' and 'status' to make the admin panel more useful
    list_display = ('user', 'bus', 'seat', 'travel_date', 'status', 'booking_time')

admin.site.register(Bus, BusAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Booking, BookingAdmin)