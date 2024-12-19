from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderItem)

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country')
    search_fields = ('shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country')
    list_filter = ('shipping_full_name', 'shipping_city', 'shipping_state')

class ShippingAddressInline(admin.StackedInline):
    extra = 0
    model = ShippingAddress

admin.site.register(ShippingAddress, ShippingAddressAdmin)



# Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

class OrderInline(admin.StackedInline):
    model = Order
    extra = 0

# Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]

# Unregister Order Model
admin.site.unregister(Order)

# Re-register our Order adn Orderadmin
admin.site.register(Order, OrderAdmin)


