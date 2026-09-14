from django.db import models
from django.utils import timezone


class BloodRequest(models.Model):
    EMERGENCY_LEVELS = [
        ('Normal', 'Normal'),
        ('Emergency', 'Emergency'),
    ]
    
    PATIENT_CONDITIONS = [
        ('Stable', 'Stable'),
        ('Critical', 'Critical'),
        ('Life Threatening', 'Life Threatening'),
        ('Surgery', 'Surgery'),
        ('Accident', 'Accident'),
        ('Maternity', 'Maternity'),
        ('Other', 'Other'),
    ]
    
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    patient_name = models.CharField(max_length=100)
    required_blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    number_of_bags = models.IntegerField(default=1)
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    patient_condition = models.CharField(max_length=20, choices=PATIENT_CONDITIONS, default='Stable')
    emergency_level = models.CharField(max_length=10, choices=EMERGENCY_LEVELS, default='Normal')
    required_date = models.DateField()
    contact_phone = models.CharField(max_length=15)
    additional_info = models.TextField(blank=True, null=True)
    request_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.patient_name} - {self.required_blood_group} - {self.emergency_level}"
    
    @property
    def is_emergency(self):
        return self.emergency_level == 'Emergency'

    @property
    def is_expired(self):
        """Feature: requests quietly age out a couple of days after the
        date blood was needed by, so the list doesn't fill up with stale
        entries. They're never deleted — just excluded from the default
        (active) listing so an admin can still audit them."""
        return self.required_date < (timezone.now().date() - timezone.timedelta(days=2))

    @property
    def response_count(self):
        return self.responses.count()

    class Meta:
        ordering = ['-request_date']


class RequestResponse(models.Model):
    """Feature: 'I'm Responding' — lets a donor signal interest in a
    specific request without the requester having to call around blindly.
    Deduplicated per logged-in donor; anonymous responders are also counted
    but not deduplicated (best-effort, no account required)."""
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='responses')
    donor = models.ForeignKey('accounts.Donor', on_delete=models.CASCADE, null=True, blank=True, related_name='responses_given')
    responder_name = models.CharField(max_length=100, blank=True)
    responder_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['request', 'donor'],
                condition=models.Q(donor__isnull=False),
                name='unique_donor_response_per_request',
            )
        ]


class Hospital(models.Model):
    """Feature: a small, admin-managed emergency contact directory.
    Deliberately NOT pre-filled with guessed/unverified private hospital
    numbers — only officially sourced numbers ship by default (see the
    0004 data migration). The site owner should add local hospitals and
    blood banks they've personally verified via the Django admin."""
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100, help_text="One or more numbers, comma-separated if needed")
    address = models.CharField(max_length=255, blank=True)
    has_blood_bank = models.BooleanField(default=False)
    is_24_7 = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order', 'name']