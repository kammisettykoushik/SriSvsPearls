from django.contrib import admin
from .models import Category, Product, Customer, Order, Profile, Testimonial
from django.contrib.auth.models import User
from payment.admin import *

# Register your models here.


admin.site.register(Customer)

admin.site.register(Profile)



def mark_as_published(modeladmin, request, queryset):
    queryset.update(is_published=True)
mark_as_published.short_description = "Mark selected products as published"

class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    list_display = ('name', 'category', 'created_at', 'price', 'is_published')
    list_filter = ('category', 'is_published', 'is_sale')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    actions = [mark_as_published]
    list_per_page = 20
    readonly_fields = ('created_at',)
    fieldsets = (('Basic Information', {'fields': ('name', 'category', 'price', 'description','image')}),
                 ('Additional Information', { 'fields': ('is_published', 'quantity', 'is_sale', 'sale_price', 'created_at'),
                                              'classes': ('collapse',) }), )
    # inlines = [ProductInline]

admin.site.register(Product, ProductAdmin)

class ProductInline(admin.TabularInline):
    model = Product
    fields = ['name', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False
    show_change_link = True
    extra = 0
    min_num = 0
    max_num = 10
    verbose_name = "Product"
    verbose_name_plural = "Products"
    list_per_page = 10

class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)




class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number')

# combine profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile


#extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline, ShippingAddressInline, OrderInline]

# Unregister the previous way
admin.site.unregister(User)
# Re-register the new way
admin.site.register(User, UserAdmin)
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'review', 'date')
    search_fields = ('name', 'review')