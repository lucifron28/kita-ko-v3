from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """
    Extended User model for Kitako platform users (informal earners in the Philippines)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)

    # Contact Information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^(\+639\d{9}|09\d{9})$',
        message="Phone number must be in format: '+639123456789' or '09123456789'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)

    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    # Work Information
    OCCUPATION_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('micro_entrepreneur', 'Micro Entrepreneur'),
        ('jeepney_driver', 'Jeepney Driver'),
        ('market_vendor', 'Market Vendor'),
        ('online_seller', 'Online Seller'),
        ('delivery_rider', 'Delivery Rider'),
        ('domestic_worker', 'Domestic Worker'),
        ('construction_worker', 'Construction Worker'),
        ('street_vendor', 'Street Vendor'),
        ('tricycle_driver', 'Tricycle Driver'),
        ('other', 'Other'),
    ]
    primary_occupation = models.CharField(
        max_length=50,
        choices=OCCUPATION_CHOICES,
        blank=True
    )
    occupation_description = models.TextField(blank=True, help_text="Describe your work")

    # Platform Settings
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('fil', 'Filipino')],
        default='en'
    )

    # Verification Status
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'kitako_users'
        verbose_name = 'Kitako User'
        verbose_name_plural = 'Kitako Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Return the user's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        """Return the user's full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.province,
            self.postal_code
        ]
        return ", ".join([part for part in address_parts if part])


class UserProfile(models.Model):
    """
    Additional profile information for users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Financial Information
    estimated_monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated monthly income in PHP"
    )

    # E-wallet Information
    has_gcash = models.BooleanField(default=False)
    has_paymaya = models.BooleanField(default=False)
    has_grabpay = models.BooleanField(default=False)
    has_coins_ph = models.BooleanField(default=False)
    has_other_ewallet = models.BooleanField(default=False)
    other_ewallet_details = models.TextField(blank=True)

    # Banking Information
    has_bank_account = models.BooleanField(default=False)
    bank_names = models.TextField(blank=True, help_text="List of banks where user has accounts")

    # Business Information (for entrepreneurs)
    business_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    business_registration_number = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kitako_user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile for {self.user.full_name}"
