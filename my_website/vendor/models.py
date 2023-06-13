# Create your models here.
from datetime import date, datetime, time
from enum import Enum

from accounts.models import User, UserProfile
from accounts.utils import send_notification
from django.db import models


class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


HOUR_OF_DAY_24 = [
    (time(hour, minute).strftime("%I:%M %p"), (time(hour, minute).strftime("%I:%M %p")))
    for hour in range(24)
    for minute in (0, 30)
]


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="user_profile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=250)
    vendor_license = models.ImageField(upload_to="vendor/license")
    vendor_slug = models.SlugField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # updated
            original = Vendor.objects.get(pk=self.pk)
            if original.is_approved != self.is_approved:
                context = {"user": self.user, "is_approved": self.is_approved}
                mail_template = "accounts/emails/admin_approval_email.html"

                if self.is_approved == True:
                    mail_subject = (
                        "Congratulations ! Your restaurant has been approved!"
                    )
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = " Your restaurant has not  approved!"
                    send_notification(mail_subject, mail_template, context)
                    ...
        return super(Vendor, self).save(*args, **kwargs)

    def is_open(self):
        today = date.today().isoweekday()
        current_open_hours = OpeningHour.objects.filter(vendor=self, day=today)
        current_time = datetime.now().time()

        for each in current_open_hours:
            start = datetime.strptime(each.from_hour, "%I:%M %p").time()
            end = datetime.strptime(each.to_hour, "%I:%M %p").time()
            if current_time > start and current_time < end:
                return True

        return False


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(
        choices=[(Weekday(day).value, Weekday(day).name) for day in Weekday]
    )
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=20, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=20, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        # Check uniqueness onf multiple fields like composite primary key
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self):
        return self.get_day_display()
