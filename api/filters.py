import django_filters
import datetime
from django.db.models import Q
from .models import Room, Booking


class RoomFilter(django_filters.FilterSet):
    capacity = django_filters.NumberFilter(field_name="capacity")
    price_per_day = django_filters.NumberFilter(field_name="price_per_day")
    check_in_date = django_filters.DateFilter(
        method="filter_by_dates", field_name="check_in_date"
    )
    check_out_date = django_filters.DateFilter(
        method="filter_by_dates", field_name="check_out_date"
    )

    class Meta:
        model = Room
        fields = ["price_per_day", "capacity"]

    def filter_by_dates(self, queryset, name, value):
        if name == "check_in_date":
            check_in_date = self.request.query_params.get("check_in_date")
            check_out_date = self.request.query_params.get("check_out_date")
            if check_in_date and check_out_date:
                try:
                    check_in_date = datetime.datetime.strptime(
                        check_in_date, "%Y-%m-%d"
                    ).date()
                    check_out_date = datetime.datetime.strptime(
                        check_out_date, "%Y-%m-%d"
                    ).date()
                    conflicting_bookings = Booking.objects.filter(
                        Q(
                            check_in_date__lte=check_out_date,
                            check_out_date__gte=check_in_date,
                        )
                    ).values_list("room_id", flat=True)

                    booked_room_ids = set(conflicting_bookings)
                    available_rooms = queryset.exclude(id__in=booked_room_ids)
                    return available_rooms
                except ValueError:
                    pass
        return queryset
