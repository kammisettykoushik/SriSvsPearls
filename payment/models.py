from django.db import models
from django.contrib.auth.models import User
from webapp.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.






#  Create Order Model

class Order(models.Model):
    # Foreign Key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=250)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default = True)
    date_shipped = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    PENDING = 'P'
    SHIPPED = 'S'
    DELIVERED = 'D'
    CANCELED = 'C'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELED, 'Canceled'),
    ]
    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES, default=PENDING)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order - {str(self.id)}'
    
    
# Auto add shipping Date when 'shipped' status is updated
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:  # Ensure the instance exists (i.e., it's not a new object)
        obj = sender._default_manager.get(pk=instance.pk)  # Get the current (old) instance
        if instance.shipped and not obj.shipped:  # If 'shipped' status is being set to True
            instance.date_shipped = timezone.now()  # Set the shipping date to current time


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  #  order = models.ForeignKey(Order, on_delete=models.CASCADE)  # This is the field you're likely missing
    shipping_full_name = models.CharField(max_length=100, null=True, blank=True)
    shipping_email = models.EmailField(max_length=100, null=True, blank=True)
    shipping_address1 = models.CharField(max_length=100, null=True, blank=True)
    shipping_address2 = models.CharField(max_length=100, null=True, blank=True)
    shipping_city = models.CharField(max_length=100, null=True, blank=True)
    shipping_state = models.CharField(max_length=100, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=100, null=True, blank=True)
    shipping_country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    #dont pluralize address
    class Meta:
        verbose_name = 'Shipping Address'

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


# create a user profile by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()


# automate the profile
post_save.connect(create_shipping, sender=User)

            


# Create Order Items Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True,
                                         blank=True)  # Make sure null=True is here

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f'Order Item - {str(self.id)}'




