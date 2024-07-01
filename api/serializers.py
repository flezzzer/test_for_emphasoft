from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Room, Booking


def room_is_available(room_id, start_date=None, end_date=None):
    if start_date and end_date:
        try:
            conflicting_bookings = Booking.objects.filter(
                room_id=room_id,
                check_in_date__lte=end_date,
                check_out_date__gte=start_date,
            )

            return not conflicting_bookings.exists()
        except ValueError:
            pass
    else:
        return True


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data):
        try:
            room_id = data.get("room")
            check_in_date = data.get("check_in_date")
            check_out_date = data.get("check_out_date")

            if not room_id or not check_in_date or not check_out_date:
                raise serializers.ValidationError({"detail": "All fields required"})

            if not room_is_available(room_id, check_in_date, check_out_date):
                raise serializers.ValidationError({"detail": "Room is not available"})

        except Room.DoesNotExist:
            raise serializers.ValidationError({"detail": "Room does not exist"})
        except ValueError as ve:
            raise serializers.ValidationError({"detail": str(ve)})
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        print(user)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return {"user": user}

    def generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
