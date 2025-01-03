from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django import forms
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart
from django.core.mail import send_mail
from django.utils import timezone

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode



# Create your views here.

def blog(request):
    return render(request, 'blog.html')
def testimonials(request):
    total_customers = Testimonial.objects.count()
    happy_customers = Testimonial.objects.filter(rating__gte=4).count()
    reviews = Testimonial.objects.all()[:5]

    context = {
        'total_customers': total_customers,
        'happy_customers': happy_customers,
        'reviews': reviews,
    }
    return render(request, 'index.html', context)


def search(request):
    query = request.GET.get('searched', '')  # Get the search query from the GET request
    sort_by = request.GET.get('sort', 'created_at')  # Default sorting by 'name'
    if query:
        # Query the Product model to find matches
        searched = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # Order the results based on the 'sort' parameter
        searched = searched.order_by(sort_by)

        # Pagination logic
        paginator = Paginator(searched, 8)  # Show 12 products per page
        page_number = request.GET.get('page')  # Get the page number from query parameters
        page_obj = paginator.get_page(page_number)

        # Check if any products were found
        if page_obj:
            return render(request, 'search.html', {'searched': page_obj, 'query': query})
        else:
            messages.error(request, "That product does not exist. Please try again.")
            return render(request, 'search.html', {'query': query})
    else:
        messages.error(request, "No Input found")
        return redirect('index')


def update_info(request):
    if request.user.is_authenticated:
        # Get current user's profile
        try:
            current_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            messages.error(request, "Profile does not exist.")
            return redirect('index')

        # Get current user's shipping info, or handle if it doesn't exist
        try:
            shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
        except ShippingAddress.DoesNotExist:
            shipping_user = None

        # Instantiate forms
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            if form_type == 'billing' and form.is_valid():
                form.save()
                messages.success(request, 'Billing address updated successfully!')
            elif form_type == 'shipping' and shipping_form.is_valid():
                shipping_form.save()
                messages.success(request, 'Shipping address updated successfully!')
            else:
                messages.error(request, 'Failed to update address.')
            return redirect('update_info')

        return render(request, "update_info.html", {
            'form': form,
            'shipping_form': shipping_form
        })

    else:
        messages.error(request, "Please login to update your account.")
        return redirect('index')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # did the form is filled?
        if request.method == 'POST':
            #proceed with it
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated!')
                #login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, 'Please login to Proceed')
        return redirect('index')


def update_user(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, request.FILES, instance=current_user)
            if user_form.is_valid():
                user_form.save()

                # Save profile picture if available
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                    profile.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('index')
        else:
            user_form = UpdateUserForm(instance=current_user)
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "Please Login to Update Your Account ")
        return redirect('index')


def category(request, foo):
    foo = foo.replace('-', '')
    try:
        category = Category.objects.get(name=foo)

        # Get the sorting option from the GET request, default to 'name'
        sort_by = request.GET.get('sort', 'created_at')  # Can be 'price', 'name', 'created_at', etc.
        products = Product.objects.filter(category=category).order_by(sort_by)

        # Add pagination here
        paginator = Paginator(products, 8)  # Adjust the number of products per page as needed
        page_number = request.GET.get('page')

        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return render(request, 'category.html', {'products': products, 'category': category, 'sort_by': sort_by})

    except:
        messages.error(request, 'That Category does not exist')
        return redirect('index')


def index(request):
    products = Product.objects.all()
    # visitor count increment by 1
    visitor_count, created = VisitorCount.objects.get_or_create(id=1)
    # visitor_count.count = 0
    # visitor_count.save()
    visitor_count.increment() # Increment the visit count
    testimonials = Testimonial.objects.all()
    total_customers_deafult = 2000
    total_customers = testimonials.count() + visitor_count.count + total_customers_deafult
    # Set default count for happy customers if no testimonials are present
    happy_customers_default = 1500  # Example default value
    happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count + happy_customers_default
    # Format counts with commas
    formatted_total_customers = "{:,}".format(total_customers)
    formatted_happy_customers = "{:,}".format(happy_customers)

    # happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count
    reviews = Testimonial.objects.all()[:5]
    return render(request, 'index.html',
                  {'products': products,
                   'testimonials': testimonials,
                   'total_customers': formatted_total_customers,
                   'happy_customers': formatted_happy_customers,
                   'reviews': reviews,
                   })


def all_products(request):
    sort_by = request.GET.get('sort', 'created_at')
    products = Product.objects.order_by(sort_by).filter(is_published=True)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)
    return render(request, 'category.html', {'products': products, 'sort_by': sort_by})


def product(request, pk):
    products = Product.objects.filter(id=pk)
    return render(request, 'product.html', {'products': products})


def special_products(request):
    products = Product.objects.all()
    return render(request, 'special-products.html', {'products': products})


def login_user(request):
    if request.method == 'POST':
        username_or_email_or_mobile = request.POST.get(
            'username_or_email_or_mobile')  # Input for username/email/mobile number
        password = request.POST['password']

        # Try to find the user by email
        user = None
        if '@' in username_or_email_or_mobile:
            user = User.objects.filter(email=username_or_email_or_mobile).first()
        elif username_or_email_or_mobile.isdigit():  # Check if it's a mobile number (purely digits)
            user = User.objects.filter(
                profile__mobile_number=username_or_email_or_mobile).first()  # Use Profile model if you have one for mobile number, else use custom method to store mobile number
        else:
            user = User.objects.filter(username=username_or_email_or_mobile).first()

        if user:
            # Check if the user's account is active (i.e., email is verified)
            if not user.is_active:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect('verify_email', username=user.username)  # Redirect to the email verification page
            # Authenticate the user
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!!!! Please Update the Profile...')
                return redirect('update_user')
            else:
                messages.error(request, 'Invalid login credentials. Please try again.')
                return redirect('login')
        else:
            messages.error(request, 'No account found with that email/phone number.')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have successfully logged out...!!"))
    return redirect('index')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the User object (this will create the user)
            user = form.save()

            # Check if the profile already exists
            profile, created = Profile.objects.get_or_create(user=user)
            mobile_number = request.POST.get('mobile_number')

            # If it's a new profile, update the mobile_number
            if mobile_number:
                profile.mobile_number = mobile_number
                profile.save()


            messages.success(request, 'Username Created - An OTP was sent to your Email...')
            return redirect('verify_email', username=user.username)

        else:
            # If form is not valid, return to the register page with errors
            for error in list(form.errors.values()):
                messages.error(request, error)
            return redirect('register')

    else:
        return render(request, 'register.html', {'form': form})

def verify_email(request, username):
    user = User.objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if request.method == 'POST':
        #valid a token
        if user_otp.otp_code == request.POST['otp_code']:

            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active=True
                user.save()
                messages.success(request, "Account activated Successfully")
                return redirect("login")
            # expired token
            else:
                messages.warning(request, "Invalid OTP entered, enter a valid OTP!!!...")
                return redirect("verify_email", username=user.username)

        # invalid otp code
        else:
            messages.warning(request, "Invalid OTp entered, enter a valid OTP!!!...")
            return redirect("verify_email", username=user.username)
    return render(request, "verify_token.html", {})

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]  # Get email from the form

        if User.objects.filter(email=user_email).exists():
            user = User.objects.get(email=user_email)

            # Check if user already has an OTP
            otp = OtpToken.objects.filter(user=user).first()

            if otp:
                # If OTP exists, you can either delete the old one or update it
                # Option 1: Delete old OTP
                otp.delete()

                # Create a new OTP token
                otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            else:
                # If no OTP exists, create a new one
                otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            # Email the OTP to the user
            subject = "Email Verification"
            message = f"""
                        Hi {user.username}, here is your OTP {otp.otp_code}
                        It expires in 5 minutes. Use the URL below to verify your email:
                        https://www.srisvspearls.com/verify_email/{user.username}
                    """
            sender = "trishokadigiservices@gmail.com"
            receiver = [user.email, ]

            # Send email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "A new OTP has been sent to your email address.")
            return redirect("verify_email", username=user.username)
        else:
            messages.warning(request, "This email doesn't exist in the database.")
            return redirect("resend-otp")
    else:
        return render(request, "resend_otp.html", {})


# password reset views before a user logged in :-





def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(str(user.pk).encode())

                # Generate password reset link
                reset_link = f"http://{get_current_site(request).domain}/reset_password/{uid}/{token}/"

                # Send email with the link
                subject = "Password Reset Request"
                message = f"Hi {user.username},\n\nYou requested a password reset. Click the link below to reset your password:\n{reset_link}\n\nIf you did not request this, ignore this message."
                send_mail(subject, message, 'trishokadigiservices@gmail.com', [user.email])

                messages.success(request, 'Password reset link sent to your email address.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Email address not found.')
                return redirect('forgot_password')
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = ResetPasswordForm(user=user)
        return render(request, 'reset_password.html', {'form': form})

    else:
        messages.error(request, 'Invalid or expired link.')
        return redirect('login')

