from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .cart import Cart
from webapp.models import Product
from django.contrib import messages
from django.http import JsonResponse
# Create your views here.
def cart_summary(request):
    if not request.user.is_authenticated:
        # Optional: Add a message to indicate the need to log in
        messages.info(request, 'Please log in to view your cart.')
        return redirect('login')

    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {"cart_products": cart_products, "quantities": quantities, "totals": totals})
def cart_add(request):
    cart = Cart(request)
    #test for post
    if request.POST.get('action') =='post':
        #GET DATA
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Ensure the quantity is at least 1
        if product_qty < 1:
            product_qty = 1

        #look product in database
        product = get_object_or_404(Product, id=product_id)

        #save to session
        cart.add(product=product, quantity=product_qty)
        #get cart quantity
        cart_quantity = cart.__len__()

        #return response
        #response = JsonResponse({'Product Name': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, 'Product added to cart')
        return response
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') =='post':
        # get data
        product_id = int(request.POST.get('product_id'))
        # call delete function in cart
        cart.delete(product=product_id)
        response = JsonResponse({'product': product_id})
        # return redirect('cart_summary')
        messages.success(request, 'Product deleted from cart')
        return response


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #GET DATA
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Ensure the quantity is at least 1
        if product_qty < 1:
            product_qty = 1

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})
        messages.success(request, 'Your Cart has been updated')
        return response
        #return redirect('cart_summary')




