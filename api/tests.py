from django.test import TestCase
from rest_framework.test import APIClient
from .serializers import RoomSerializer
from .models import Room, Booking, User


class RoomListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rooms = Room.objects.bulk_create(
            [
                Room(name="Luxury Suite", price_per_day=200, capacity=4),
                Room(name="Standard Room", price_per_day=100, capacity=2),
            ]
        )

    def test_get_rooms(self):
        response = self.client.get("/api/v1/rooms/")
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)


class BookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.room = Room.objects.create(name="Test Room", price_per_day=100, capacity=2)
        self.booking_data = {
            "room": self.room.id,
            "check_in_date": "2024-07-01",
            "check_out_date": "2024-07-10",
            "status": False,
            "user": self.user.id,
        }

    def test_create_booking(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/v1/{self.user}/bookings/", data=self.booking_data
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Booking.objects.exists())


class UserLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_login_success(self):
        response = self.client.post(
            "/api/v1/login/", {"username": "testuser", "password": "testpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_new_user(self):
        response = self.client.post(
            "/api/v1/registration/", {"username": "newuser", "password": "newpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
