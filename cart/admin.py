# from django.contrib import admin
# from webapp.models import *
# from payment.models import *
# from webapp.admin import *
# from payment.admin import *
# from django.urls import path
# from django.shortcuts import render
# from django.db.models import Sum
# import plotly.express as px
#
# class CustomAdmin(admin.ModelAdmin):
#     def get_urls(self):
#         urls = super().get_urls()  # Get default admin URLs
#         custom_urls = [
#             path('analytics/', self.admin_view(self.analytics_view), name='analytics')  # Custom URL for analytics
#         ]
#         return custom_urls + urls  # Make sure custom URLs are placed at the top
#
#     def analytics_view(self, request):
#         # Aggregating the data for the analytics
#         orders = Order.objects.all()
#         total_sales = orders.aggregate(Sum('total'))['total__sum']
#         total_orders = orders.count()
#
#         # Visualize Product Sales
#         products = Product.objects.all()
#         product_sales = products.values('name').annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold')
#
#         # Using Plotly to create a bar chart for product sales
#         fig = px.bar(product_sales, x='name', y='total_sold', title='Product Sales')
#         graph_html = fig.to_html(full_html=False)
#
#         # Render the template for the analytics page in the admin interface
#         context = {
#             'total_sales': total_sales,
#             'total_orders': total_orders,
#             'graph_html': graph_html,
#         }
#
#         return render(request, 'admin/analytics.html', context)
