import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from webapp.views import *
from django.urls import reverse
from django.core.mail import BadHeaderError





# def verify_otp(request):
#     if request.method == 'POST':
#         otp_entered = request.POST['otp']
#         user = request.user
#         try:
#             # Fetch OTP verification object for the current user
#             email_verification = EmailVerification.objects.get(user=request.user)
#
#             #check if OTp matches and if it's not expired
#             if email_verification.otp == otp_entered and not email_verification.is_expired():
#                 email_verification.is_verified = True
#                 email_verification.save()
#
#                 messages.success(request, 'Email verified successfully')
#                 return redirect('index')
#             else:
#                 messages.success(request, 'Invalid or expired OTP. Please try again.')
#                 return redirect('verify_email')
#
#         except EmailVerification.DoesNotExist:
#             messages.error(request, 'No verification OTP found for your account. ')
#             return redirect('register')
#     return render(request, 'verify_email.html')

