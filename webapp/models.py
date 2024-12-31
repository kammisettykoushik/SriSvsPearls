from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
import secrets

# Create your models here.


# create Customer profile
class Profile(models.Model):
    DoesNotExist = None
    objects = None
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_modified = models.DateTimeField(User, auto_now=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username


# create a user profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()


# automate the profile
post_save.connect(create_profile, sender=User)


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

    def get_products(self):
        return self.product_set.all()


class Product(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    quantity = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)
    address = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=13)
    date = models.DateField(default=datetime.today, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product


class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.PositiveIntegerField()  # Assuming a rating out of 5
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"

    def filled_stars(self):
        return range(self.rating)

    def empty_stars(self):
        return range(5 - self.rating)


class VisitorCount(models.Model):
    count = models.PositiveIntegerField(default=50)

    def increment(self):
        self.count += 1
        self.save()

    def __str__(self):
        return f"Visit Count: {self.count}"


# email verification models start here :-

# Function to generate the OTP code
def generate_otp():
    return secrets.token_hex(3)

class OtpToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6, default=generate_otp)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
