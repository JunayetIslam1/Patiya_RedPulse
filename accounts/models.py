from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string


def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    AVAILABILITY_STATUS = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.IntegerField()
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    last_donation_date = models.DateField()
    availability_status = models.CharField(max_length=15, choices=AVAILABILITY_STATUS, default='Available')
    registration_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    # Feature: profile photo (builds trust — a directory of faceless phone
    # numbers is less trustworthy than one with real donor photos).
    photo = models.ImageField(upload_to='donor_photos/', blank=True, null=True)

    # Feature: optional location, set once via the browser's geolocation
    # ("Use my location" button) so search results can be sorted by actual
    # distance instead of an exact-text district/upazila match.
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Feature: referral program. Every donor gets a unique code; anyone who
    # registers through that donor's link/code is credited to them, which
    # both the donor and the whole platform can see recognised.
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals'
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = generate_referral_code()
            while Donor.objects.filter(referral_code=code).exists():
                code = generate_referral_code()
            self.referral_code = code
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.blood_group}"
    
    @property
    def days_since_last_donation(self):
        today = timezone.now().date()
        return (today - self.last_donation_date).days

    @property
    def eligibility_gap_days(self):
        """
        Minimum gap required between two donations, per Bangladesh Red
        Crescent / DGHS transfusion guidance: 90 days for male donors,
        120 days for female donors (women need a longer recovery window).
        """
        return 90 if self.gender == 'Male' else 120

    @property
    def is_eligible(self):
        return self.days_since_last_donation >= self.eligibility_gap_days
    
    @property
    def days_until_eligible(self):
        """পরবর্তী রক্তদানের জন্য কতদিন বাকি তা হিসেব করবে"""
        if self.is_eligible:
            return 0
        return self.eligibility_gap_days - self.days_since_last_donation

    @property
    def eligibility_status(self):
        if self.is_eligible:
            return "Eligible to Donate"
        else:
            return f"Not Eligible ({self.days_until_eligible} days remaining)"

    @property
    def donation_count(self):
        return self.donations.count()

    @property
    def lifesaver_tier(self):
        """
        Feature: recognise repeat donors with a simple tier badge, using the
        DonationHistory records that already existed in the data model but
        weren't surfaced anywhere in the UI.
        """
        count = self.donation_count
        if count >= 6:
            return 'gold'
        if count >= 3:
            return 'silver'
        if count >= 1:
            return 'bronze'
        return 'new'

    @property
    def referral_count(self):
        return self.referrals.count()

    @property
    def referral_tier(self):
        count = self.referral_count
        if count >= 5:
            return 'champion'
        if count >= 1:
            return 'builder'
        return 'none'

    def distance_km_from(self, lat, lng):
        """Haversine distance in km, or None if this donor has no location set."""
        if self.latitude is None or self.longitude is None:
            return None
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(radians, [lat, lng, self.latitude, self.longitude])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))
    
    class Meta:
        ordering = ['-registration_date']

class DonationHistory(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateField()
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.full_name} - {self.donation_date}"

    class Meta:
        ordering = ['-donation_date']
