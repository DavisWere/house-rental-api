import django
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
import os
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

phone_validator = RegexValidator(r"^\d{9,10}$", "Enter a valid phone number.")

phone_code_validator = RegexValidator(r"^\+\d{1,3}$")


class UtilColumnsModel(models.Model):
    """Abstract model for created_at & updated_at fields."""

    created_at = models.DateTimeField(
        default=django.utils.timezone.now, null=True, blank=True
    )
    updated_at = models.DateTimeField(
        blank=True, null=True, default=django.utils.timezone.now
    )
    is_active = models.BooleanField(default=True)


class Company(UtilColumnsModel):
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=50)
    logo = models.ImageField(null=True, blank=True)
    location = models.CharField(null=True, blank=True, max_length=300)
    box_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_code = models.CharField(
        max_length=4, validators=[phone_code_validator], blank=True, null=True
    )
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
    phone_number = models.CharField(
        max_length=10, validators=[phone_validator], blank=True, null=True, unique=True
    )


class Tenant(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length= 20, unique=True)
    ID_TYPE_CHOICES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        # any other id_type if needed
    ]
    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES, default='national_id')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Property(models.Model):
    name = models.CharField(max_length=50)
    owner = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True)
    reg_number = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class UnitType(models.Model):
    rooms = models.CharField(max_length=255)
    bathrooms = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=None)
    base_price = models.FloatField()
    service_charge = models.FloatField(default=0)
    min_water_charge = models.FloatField(default=0)
    grace_period_days = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.rooms} Rooms, {self.bathrooms} Bathrooms @ksh ({self.base_price})"


class Utilities(UtilColumnsModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class PropertyUnit(models.Model):
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    rent_amount = models.FloatField()
    unit_number = models.CharField(max_length=30)

    def __str__(self):
        return f"Unit {self.unit_number} ({self.unit_type}), Property: {self.property.name}"


class FixedUnitCharge(models.Model):
    name = models.CharField(max_length=50)
    amount = models.FloatField()
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


RENT_FREQUENCY_CHOICES = [
    ('days', 'Days'),
    ('month', 'Month'),
]


class TenantPropertyUnit(models.Model):
    rent_amount = models.FloatField()
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    rent_frequency_number = models.PositiveIntegerField()
    rent_frequency_type = models.CharField(max_length=20, choices=RENT_FREQUENCY_CHOICES)
    property_unit = models.ForeignKey(PropertyUnit, on_delete=models.CASCADE)
    start_date = models.DateField(default=datetime.now)
    next_billing_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Tenant: {self.tenant}, Property Unit: {self.property_unit}"


UTILITY_TYPES = (
    ("water", "Water"),
    ("electricity", "Electricity"),
    ("service_charge", "Service Charge"),
    ("rent", "Rent"),
    ("damages", "Damages"),
    ("fixed_charge", "Fixed Charges"),
)


class Invoice(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant_unit = models.ForeignKey(TenantPropertyUnit, on_delete=models.CASCADE)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    account_number = models.CharField(max_length=250, null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('void', 'Void'),
    ], default='unpaid')

    def __str__(self):
        return f"Invoice ID: {self.id}, Status: {self.status}"


class TenantPropertyUnitsUtilities(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=255, choices=UTILITY_TYPES)
    amount = models.FloatField()
    tenant_property_unit = models.ForeignKey(TenantPropertyUnit, on_delete=models.CASCADE)
    pre_reading = models.CharField(max_length=20, null=True, blank=True)
    current_reading = models.CharField(max_length=20, null=True, blank=True)
    charge_date = models.DateField()
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name


INVOICE_ITEM_TYPES_CHOICES = [
    ('utility', 'Utility'),
    ('rent', 'Rent'),
    ('fixed_charges', 'Fixed Charges'),
]


# todo : remove invoice items
class InvoiceItems(models.Model):
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    item_type = models.CharField(max_length=20, choices=INVOICE_ITEM_TYPES_CHOICES)

    def __str__(self):
        return f"Item: {self.name}, Amount: {self.amount}"


class InvoicePayment(UtilColumnsModel):
    name = models.CharField(max_length=30)


TRANSACTION_STATUS_CHOICES = (
    ("processing", "Processing"),
    ("processed", "Processed"),
    ("failed", "Failed"),
)


class Transaction(models.Model):
    customer_account_number = models.CharField(max_length=40)
    amount = models.FloatField()
    utilized_amount = models.FloatField(default=0)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True)
    transaction_code = models.CharField(
        max_length=255, unique=True, null=True
    )  # Mpesa code after a payment is complete
    transaction_status = models.CharField(
        max_length=20, choices=TRANSACTION_STATUS_CHOICES, default="processing"
    )
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    transaction_timestring = models.CharField(max_length=255, null=True, blank=True)
    transaction_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.pk}"
    
class InvoiceTransaction(models.Model):
    transaction_type = models.CharField(max_length=50)
    trans_id = models.CharField(max_length=255, unique=True)
    trans_time = models.DateTimeField(max_length=50)
    trans_amount = models.FloatField()
    business_short_code = models.CharField(max_length=50)
    bill_ref_number = models.CharField(max_length=50)
    invoice_number = models.CharField(max_length=50, unique=True)
    org_account_balance = models.DecimalField(max_digits=10, decimal_places=2)
    third_party_trans_id = models.CharField(max_length=50)
    MSISDN = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return self.trans_id


CHANNEL_TYPES_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('sms', 'Sms'),
    ('push_notification', 'Push Notification'),
]



class Notification(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES_CHOICES)
    channel = models.CharField(max_length=255)
    sent = models.BooleanField(default=False)
    retries = models.PositiveIntegerField(default=0)
    contents = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Notification {self.pk}"
