import logging
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            ip = self.get_client_ip(request)
            current_time = timezone.now()
            path = request.path
            logger.info(f"Admin access attempt: IP={ip}, Path={path}, Time={current_time}")
            if not self.is_allowed_ip(ip):
                logger.warning(f"Forbidden access attempt: IP={ip}")
                self.send_alert(ip, path, current_time)
                response = render_to_string('403.html')
                return HttpResponseForbidden(response)
        return self.get_response(request)

    def get_client_ip(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_allowed_ip(self, ip):
        allowed_ips = ['192.168.0.109', '127.0.0.1']  # Add your trusted IPs here
        return ip in allowed_ips

    def send_alert(self, ip, path, current_time):
        subject = 'Unauthorized Admin Access Attempt at SriSvsPearls'
        from_email = 'omprakashmadasi@gmail.com'
        to_email = 'trishokadigiservices@gmail.com'

        context = {
            'ip': ip,
            'path': path,
            'current_time': current_time,
        }

        html_content = render_to_string('email_template.html', context)
        text_content = f"""
        Dear Admin,

        There was an unauthorized attempt to access the admin page of SriSvsPearls.

        Details:
        IP Address: {ip}
        Path: {path}
        Time: {current_time}

        Please take the necessary actions to secure your website.
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# class AdminAccessMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         if request.path.startswith('/admin/') and not self.is_allowed_ip(request):
#             return HttpResponseForbidden('Forbidden')
#         return self.get_response(request)
#
#     def is_allowed_ip(self, request):
#         allowed_ips = ['192.168.0.109', '127.0.0.1']  # Include local IP and localhost
#         ip = request.META.get('HTTP_X_FORWARDED_FOR')
#         if ip:
#             ip = ip.split(',')[0]  # In case of multiple forwarded IPs, take the first one
#         else:
#             ip = request.META.get('REMOTE_ADDR')
#
#         logger.info(f"Client IP: {ip}")
#         logger.info(f"Allowed IPs: {allowed_ips}")
#         return ip in allowed_ips
