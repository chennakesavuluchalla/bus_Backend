from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserRegisterSerializer, BusSerializer, BookingSerializer, UserSerializer
from .models import Bus, Seat, Booking

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    
class BusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    
class BookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        seat_id = request.data.get('seat')
        booking_from = request.data.get('booking_from')
        booking_to = request.data.get('booking_to')
        total_fare = request.data.get('total_fare')
        travel_date = request.data.get('travel_date')

        if not travel_date:
            return Response({'error': 'Travel date is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seat = Seat.objects.get(id=seat_id)
            
            # 🚨 FIXED: Added .exclude(status='CANCELLED') so cancelled seats can be re-booked
            if Booking.objects.filter(seat=seat, travel_date=travel_date).exclude(status='CANCELLED').exists():
                return Response({'error': 'Seat already booked for this date'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking = Booking.objects.create(
                user=request.user,
                bus=seat.bus,
                seat=seat,
                booking_from=booking_from or seat.bus.starting_at,
                booking_to=booking_to or seat.bus.destination,
                total_fare=total_fare or seat.bus.price,
                travel_date=travel_date,
                status='CONFIRMED'
            )
            
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Seat.DoesNotExist:
            return Response({'error': 'Invalid Seat ID'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        bookings = Booking.objects.filter(user_id=user_id).order_by('-booking_time')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

# ==========================================
# USER PROFILE VIEW FOR DASHBOARD
# ==========================================
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, user_id):
        if request.user.id != user_id:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ==========================================
# CANCEL BOOKING VIEW
# ==========================================
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            
            if booking.status == 'CANCELLED':
                return Response({'error': 'Booking is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

            booking.status = 'CANCELLED'
            booking.save()

            return Response({'message': 'Ticket cancelled successfully. Refund initiated.'}, status=status.HTTP_200_OK)
            
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)