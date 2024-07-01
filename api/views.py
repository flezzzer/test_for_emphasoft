from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Room, Booking
from django.contrib.sessions.models import Session
from django.urls import reverse_lazy
from .serializers import RoomSerializer, BookingSerializer
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .permissions import IsAdminUserOrReadOnly
from .filters import RoomFilter


class RoomListView(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RoomFilter
    ordering_fields = ["price_per_day", "capacity"]
    permission_classes = [IsAdminUserOrReadOnly]


class BookingViewSet(ModelViewSet):

    queryset = Booking.objects.none()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        username = self.kwargs["username"]
        return Booking.objects.filter(user__username=username)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("User registration data:", request.data)
        print("Validated user data:", serializer.validated_data)
        user = serializer.validated_data["user"]
        login(request, user)
        refresh = RefreshToken.for_user(user)

        session_key = request.session.session_key
        Session.objects.get(session_key=session_key).session_key = refresh.access_token

        username = user.username
        redirect_url = reverse_lazy("booking-list", kwargs={"username": username})

        return Response(
            {
                "user": UserLoginSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "redirect_url": redirect_url,
            }
        )


class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        refresh = RefreshToken.for_user(user)
        print("User registration data:", request.data)
        print("Validated user data:", serializer.validated_data)
        return Response(
            {
                "user": UserRegistrationSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
