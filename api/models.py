from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.room}+{self.user}"
