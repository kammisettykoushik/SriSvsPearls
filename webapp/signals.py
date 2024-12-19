from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import *
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            # Create OTP token
            otp = OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            print(f"OTP Created: {otp.otp_code} for user {instance.username}")  # Debugging: Ensure OTP is created

            instance.is_active = False
            instance.save()

            # Prepare the email
            subject = "Email Verification"
            message = f"""
                Hi {instance.username}, here is your OTP {otp.otp_code}
                It expires in 5 minutes. Use the link below to verify your email:
                http://127.0.0.1:8000/verify-email/{instance.username}
            """
            sender_email = "omprakashmadasi@gmail.com"  # Replace with your email
            recipient_list = [instance.email]

            print(f"Sending OTP to: {instance.email}")  # Debugging: Ensure the email is going to the correct address

            try:
                # Send the email
                send_mail(
                    subject,
                    message,
                    sender_email,
                    recipient_list,
                    fail_silently=False,  # This will raise an error if sending fails
                )
                print(f"OTP Sent successfully to {instance.email}")  # Debugging: Verify the email is sent
            except Exception as e:
                print(f"Error sending email: {e}")  # Debugging: Log any errors in email sending
