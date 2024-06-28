from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from django.db.models import Q
import datetime
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


def room_is_available(start_date=None, end_date=None):
    if start_date and end_date:
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

            conflicting_bookings = Booking.objects.filter(
                Q(check_in_date__lte=end_date, check_out_date__gte=start_date)  # ?
            ).values_list("room_id", flat=True)

            booked_room_ids = set(
                conflicting_bookings.values_list("room_id", flat=True)
            )
            available_rooms = Room.objects.exclude(id__in=booked_room_ids).all()
            return available_rooms
        except ValueError:
            pass
    else:
        return Room.objects.all()


class RoomListView(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filterset_fields = ["price_per_day", "capacity"]
    ordering_fields = ["price_per_day", "capacity"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    search_fields = ["capacity", "price_per_day"]
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        sorting_param = self.request.query_params.get("sort_by", None)
        if sorting_param == "by_price":
            queryset = queryset.order_by("price_per_day")
        elif sorting_param == "by_capacity":
            queryset = queryset.order_by("capacity")

        start_date = self.request.query_params.get("check_in_date", None)
        end_date = self.request.query_params.get("check_out_date", None)
        available_rooms = room_is_available(start_date, end_date)
        queryset = queryset.filter(Q(pk__in=available_rooms))
        return queryset

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]


class BookingViewSet(ModelViewSet):

    queryset = Booking.objects.none()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        username = self.kwargs["username"]
        return Booking.objects.filter(user__username=username)

    def perform_create(self, serializer):
        room_id = self.request.data.get("room")
        check_in_date = self.request.data.get("check_in_date")
        check_out_date = self.request.data.get("check_out_date")

        try:
            room = Room.objects.get(id=room_id)
            if room not in room_is_available(check_in_date, check_out_date):
                raise ValueError("Room is not available")
            serializer.save(
                user=self.request.user,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
            )
        except Exception as e:
            raise e


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
