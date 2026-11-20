from rest_framework import serializers
from .models import Bus, Seat, Booking, UserProfile 
from django.contrib.auth.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user
    
class SeatSerializer(serializers.ModelSerializer):
    # Use a dynamic method to calculate is_booked
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_booked']

    def get_is_booked(self, obj):
        # Get the request context to access the ?date= parameter
        request = self.context.get('request')
        travel_date = request.query_params.get('date') if request else None
        
        # If no date is selected, assume seat is available
        if not travel_date:
            return False 
            
        # 🚨 FIX: Check for active bookings only (exclude CANCELLED)
        return Booking.objects.filter(
            seat=obj, 
            travel_date=travel_date
        ).exclude(status='CANCELLED').exists()

class BusSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to pass context to seats
    seats = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = '__all__'

    def get_seats(self, obj):
        seats = obj.seats.all()
        # Pass the context (which contains the request) to the SeatSerializer
        return SeatSerializer(seats, many=True, context=self.context).data
        
class BookingSerializer(serializers.ModelSerializer):
    bus = BusSerializer(read_only=True) 
    seat = SeatSerializer()
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'booking_time', 'bus', 'seat']
        
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['id', 'username']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            if instance.profile.profile_picture:
                data['profile_picture'] = instance.profile.profile_picture.url
            else:
                data['profile_picture'] = None
        except UserProfile.DoesNotExist:
            data['profile_picture'] = None
        return data

    def update(self, instance, validated_data):
        profile_pic = validated_data.pop('profile_picture', None)
        
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if profile_pic:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            profile.profile_picture = profile_pic
            profile.save()

        return instance