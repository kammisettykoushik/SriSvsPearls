from django.urls import path
from . import views
urlpatterns = [

    path('checkout', views.checkout, name='checkout'),
    path('billing_info', views.billing_info, name='billing_info'),
    path('process_order', views.process_order, name='process_order'),
    path('invoice/<int:order_id>', views.generate_invoice, name='generate_invoice'),
    path('payment', views.payment_view, name='payment'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('orders', views.orders_summary, name='orders_summary'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),  # Individual order details page
    



]