from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from webapp.models import Product
from webapp.models import Profile
from webapp.forms import UserInfoForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from urllib.parse import quote
#from payment.razorpay_integration import initiate_payment
# Create your views here.
def payment_view(request):
    amount = 100 # Set the amount dynamically or based on your requirements
    order_id = initiate_payment(amount)
    context = {
        'order_id': order_id,
        'amount': amount
    }
    return render(request, 'payment.html', context)


def payment_success_view(request):
   order_id = request.POST.get('order_id')
   payment_id = request.POST.get('razorpay_payment_id')
   signature = request.POST.get('razorpay_signature')
   params_dict = {
       'razorpay_order_id': order_id,
       'razorpay_payment_id': payment_id,
       'razorpay_signature': signature
   }
   try:
       client.utility.verify_payment_signature(params_dict)
       # Payment signature verification successful
       # Perform any required actions (e.g., update the order status)
       return render(request, 'payment_success.html')
   except razorpay.errors.SignatureVerificationError as e:
       # Payment signature verification failed
       # Handle the error accordingly
       return render(request, 'payment_failure.html')


@login_required
def orders_summary(request):
    # Fetch all orders for the logged-in user
    orders = Order.objects.filter(user=request.user)

    # Calculate the total price for each order if it's not already calculated in the model
    for order in orders:
        order.total_price = sum(item.price * item.quantity for item in OrderItem.objects.filter(order=order))

    return render(request, 'user_orders.html', {'orders': orders})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Calculate total price for each order item
    for item in order_items:
        item.total_price = item.price * item.quantity

    shipping_address = ShippingAddress.objects.filter(user=order.user).first()
    if not shipping_address:
        shipping_address = None  # or handle the case accordingly

    return render(request, 'order_details.html', {
        'order': order,
        'shipping_address': shipping_address,
        'order_items': order_items,
    })


@login_required
def generate_invoice(request, order_id):
    # Get the order from the database
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Get the shipping address related to the order
    shipping_address = ShippingAddress.objects.filter(user=order.user).first()

    # Calculate total price for each order item
    for item in order_items:
        item.total_price = item.price * item.quantity

    # If no shipping address exists, handle gracefully
    if not shipping_address:
        shipping_address = None  # or some default data handling

    # Check if the PDF download button was clicked
    if request.method == 'POST' and 'download_pdf' in request.POST:
        # Create the PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

        # Create the PDF using ReportLab
        pdf_canvas = canvas.Canvas(response, pagesize=letter)
        page_width, page_height = letter

        # Add logo image
        logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTGyCO91mL-I72BnfATM3SzjMMBMTjgKXt36g&s"
        logo = ImageReader(logo_url)
        pdf_canvas.drawImage(logo, 20, 740, width=50, height=50)  # Adjust position and size as needed
        pdf_canvas.setFont("Helvetica-Bold", 16)
        pdf_canvas.drawString(200, 750, f"Invoice for your order:")

        pdf_canvas.setFont("Helvetica", 10)
        pdf_canvas.drawString(30, 730, f"Order Date: {order.created_at.strftime('%B %d, %Y')}")
        pdf_canvas.drawString(30, 715, f"Invoice Number: {order.id}")

        pdf_canvas.setStrokeColor(colors.black)
        pdf_canvas.setLineWidth(1)
        pdf_canvas.line(30, 705, page_width - 30, 705)

        if shipping_address:
            pdf_canvas.setFont("Helvetica-Bold", 12)
            pdf_canvas.drawString(30, 680, "Shipping Info:")
            pdf_canvas.setFont("Helvetica", 10)
            pdf_canvas.drawString(30, 665, f"Name: {shipping_address.shipping_full_name}")
            pdf_canvas.drawString(30, 650, f"Email: {shipping_address.shipping_email}")
            pdf_canvas.drawString(30, 635,
                                  f"Address: {shipping_address.shipping_address1}, {shipping_address.shipping_address2}")
            pdf_canvas.drawString(30, 620, f"City: {shipping_address.shipping_city}")
            pdf_canvas.drawString(30, 605, f"State: {shipping_address.shipping_state}")
            pdf_canvas.drawString(30, 590, f"Zipcode: {shipping_address.shipping_zipcode}")
            pdf_canvas.drawString(30, 575, f"Country: {shipping_address.shipping_country}")
        else:
            pdf_canvas.setFont("Helvetica", 10)
            pdf_canvas.drawString(30, 665, "Shipping information not available")

        pdf_canvas.line(30, 560, page_width - 30, 560)

        # Add the order items in a table-like format
        y_position = 540
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(30, y_position, "Product")
        pdf_canvas.drawString(250, y_position, "Price")
        pdf_canvas.drawString(350, y_position, "Quantity")
        pdf_canvas.drawString(450, y_position, "Total")

        pdf_canvas.setFont("Helvetica", 10)
        y_position -= 20

        for item in order_items:
            item_total_price = item.price * item.quantity
            pdf_canvas.drawString(30, y_position, item.product.name)
            pdf_canvas.drawString(250, y_position, f"${item.price:.2f}")
            pdf_canvas.drawString(350, y_position, str(item.quantity))
            pdf_canvas.drawString(450, y_position, f"${item_total_price:.2f}")

            y_position -= 20

        pdf_canvas.line(30, y_position, page_width - 30, y_position)

        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(350, y_position - 20, f"Total Amount Paid: ${order.amount_paid:.2f}")
        pdf_canvas.line(30, y_position - 30, page_width - 30, y_position - 30)
        pdf_canvas.showPage()
        pdf_canvas.save()
        return response
    return render(request, 'invoice_template.html', {
        'order': order,
        'shipping_address': shipping_address,
        'order_items': order_items,
    })




def process_order(request):
    if request.method == 'POST':
        print("POST request received")

        # Get cart Info
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get shipping session data
        shipping_info = request.session.get('shipping_info')
        print("Shipping info:", shipping_info)

        # Gather Order Info
        full_name = shipping_info['shipping_full_name']
        email = shipping_info['shipping_email']
        shipping_address = f"{shipping_info['shipping_address1']}\n{shipping_info['shipping_address2']}\n{shipping_info['shipping_city']}\n{shipping_info['shipping_zipcode']}\n{shipping_info['shipping_country']}"
        amount_paid = totals

        # Build the WhatsApp message with professional UI
        message = f"*Order Inquiry* \n\n"

        message += f"👤 *Customer Details*:\n"
        message += f"• *Full Name*: {full_name}\n"
        message += f"• *Email*: {email}\n\n"

        message += f"🏠 *Shipping Address*:\n"
        message += f"{shipping_address}\n\n"

        message += f"💲 *Total Amount*: ₹{amount_paid}\n\n"

        message += f"📦 *Order Details*:\n"

        for product in cart_products():
            product_name = product.name
            product_quantity = quantities().get(str(product.id), 1)  # Default to 1 if not found
            product_price = product.sale_price if product.is_sale else product.price
            message += f"• *{product_name}* x {product_quantity} - ₹{product_price} each\n"

        # URL encode the message for WhatsApp
        encoded_message = quote(message)

        # Create the WhatsApp URL
        whatsapp_url = f"https://wa.me/+919100177915?text={encoded_message}"

        # Redirect to WhatsApp
        return redirect(whatsapp_url)

    else:
        print("Access Denied: Invalid request method")
        messages.error(request, 'Access Denied')
        return redirect('billing_info')


def billing_info(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Retrieve shipping info from session
    shipping_info = request.session.get('shipping_info', {})

    if request.method == 'POST':
        if 'pay_now' in request.POST:
            # Handle the payment process
            return redirect('process_order')  # Redirect to the order processing view
        elif 'cancel' in request.POST:
            # Handle the cancellation process
            messages.info(request, "Order cancelled.")
            return redirect('index')  # Redirect to the home page

    return render(request, 'billing_info.html', {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_info": shipping_info,
    })


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        try:
            user = User.objects.get(id=request.user.id)
            profile = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            messages.error(request, "Profile does not exist.")
            return redirect('index')

        billing_form = UserInfoForm(request.POST or None, instance=profile)
        shipping_form = ShippingForm(request.POST or None)

        if request.method == 'POST':
            if billing_form.is_valid():
                billing_form.save()
                if 'shipDifferentAddress' in request.POST:
                    if shipping_form.is_valid():
                        shipping_address, created = ShippingAddress.objects.update_or_create(
                            user=request.user,
                            defaults={
                                'shipping_full_name': shipping_form.cleaned_data['shipping_full_name'],
                                'shipping_email': shipping_form.cleaned_data['shipping_email'],
                                'shipping_address1': shipping_form.cleaned_data['shipping_address1'],
                                'shipping_address2': shipping_form.cleaned_data['shipping_address2'],
                                'shipping_city': shipping_form.cleaned_data['shipping_city'],
                                'shipping_state': shipping_form.cleaned_data['shipping_state'],
                                'shipping_zipcode': shipping_form.cleaned_data['shipping_zipcode'],
                                'shipping_country': shipping_form.cleaned_data['shipping_country']
                            }
                        )
                        request.session['shipping_info'] = request.POST.dict()
                    else:
                        messages.error(request, "Invalid shipping address form")
                        return redirect('checkout')
                else:
                    # Save billing info as shipping info
                    shipping_info = {
                        'shipping_full_name': user.username,
                        'shipping_email': user.email,
                        'shipping_address1': profile.address1,
                        'shipping_address2': profile.address2,
                        'shipping_city': profile.city,
                        'shipping_state': profile.state,
                        'shipping_zipcode': profile.zipcode,
                        'shipping_country': profile.country
                    }
                    request.session['shipping_info'] = shipping_info
                    ShippingAddress.objects.update_or_create(
                        user=request.user,
                        defaults=shipping_info
                    )

                return redirect('billing_info')

        return render(request, 'checkout.html', {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "billing_form": billing_form,
            "shipping_form": shipping_form,
        })
    else:
        shipping_form = ShippingForm(request.POST or None)
        if request.method == 'POST' and shipping_form.is_valid():
            shipping_form.save()
            return redirect('billing_info')

        return render(request, 'checkout.html', {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form,
        })

def payment_success(request):
    return render(request, 'payment_success.html')
