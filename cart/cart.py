from webapp.models import Product, Profile
from decimal import Decimal
from django.contrib import messages


class Cart():
    def __init__(self, request):
        self.session = request.session
        #get request
        self.request = request

        #get the current session key if it exists
        cart = self.session.get('session_key')

        # if the user is new, no session key! create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        #make sure that cart is available on all pages of site
        self.cart = cart

    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)
        # logic
        if product_id in self.cart:
            pass
        else:

            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        # dealing with logged in user
        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert to string json
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # save carty to profile model
            current_user.update(old_cart=str(carty))

    def add(self, product, quantity=1):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            self.cart[product_id] += int(quantity)
        else:
            #    self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        #dealing with logged in user
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert to string json
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # save carty to profile model
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        # get product IDS
        product_ids = self.cart.keys()
        # lookup to those keys on products database model
        products = Product.objects.filter(id__in=product_ids)
        # get quantities
        quantites = self.cart
        # start counting at 0
        total = Decimal('0.0')  # inisialize total , Decimal
        for key, value in quantites.items():
            # convert key string into to do math
            key = int(key)
            for product in products:
                qty = Decimal(value)  # Convert value para Decimal
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * qty)
                    else:
                        total = total + (product.price * qty)
        return total

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # get ids rom cart
        product_ids = self.cart.keys()
        # use ids to look from database model
        products = Product.objects.filter(id__in=product_ids)
        # return those products
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)
        #get cart
        ourcart = self.cart
        #update json dictionary/cart
        ourcart[product_id] = product_qty
        self.session.modified = True

        # dealing with logged-in user
        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert to string json
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # save carty to profile model
            current_user.update(old_cart=str(carty))

        thing = self.cart
        return thing

    def delete(self, product):
        product_id = str(product)
        #delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True

        # dealing with logged-in user
        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert to string json
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            # save carty to profile model
            current_user.update(old_cart=str(carty))
