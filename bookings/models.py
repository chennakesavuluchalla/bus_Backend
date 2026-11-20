from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Bus(models.Model):
    bus_name = models.CharField(max_length=100)
    bus_number = models.CharField(max_length=20,unique=True)
    starting_at = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    features = models.TextField()
    start_time = models.TimeField()
    reach_time = models.TimeField()
    no_of_seats = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    
    # 🚨 Field to store intermediate stops (e.g., ["Gudur", "Nellore"])
    stops = models.JSONField(default=list, blank=True) 

    def __str__(self):
        return f'{self.bus_name} {self.bus_number} {self.starting_at} - {self.destination} '
    
    
class Seat(models.Model):
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    # 🚨 REMOVED: is_booked = models.BooleanField(default=False)
    # We no longer use this because seat availability is calculated dynamically by travel date.
    
    def __str__(self):
            return f'{self.bus} {self.seat_number}'
        
        
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    
    # Fields to save the exact route and price the user selected
    booking_from = models.CharField(max_length=100, null=True, blank=True)
    booking_to = models.CharField(max_length=100, null=True, blank=True)
    total_fare = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    travel_date = models.DateField(null=True, blank=True)

    # 🚨 ADDED: Booking status for the payment flow
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'{self.user.username}-{self.bus.bus_name}-{self.bus.start_time}-{self.bus.reach_time}-{self.seat.seat_number}'
        

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"