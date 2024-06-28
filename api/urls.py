from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomListView, BookingViewSet, UserLoginView, UserRegistrationView


router1 = DefaultRouter()


router1.register(r"rooms", RoomListView, basename="room")
router1.register(r"(?P<username>\w+)/bookings", BookingViewSet, basename="booking")


urlpatterns = [
    path("", include(router1.urls)),
    # path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path("login/", UserLoginView.as_view()),
    path("registration/", UserRegistrationView.as_view()),
]
