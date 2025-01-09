
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



