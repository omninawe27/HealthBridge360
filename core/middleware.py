import time
import logging
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create cache key
        cache_key = f'rate_limit_{ip}'
        current_time = int(time.time())

        # Get current requests
        requests = cache.get(cache_key, [])

        # Remove old requests outside the window
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        requests = [req_time for req_time in requests if req_time > window_start]

        # Check if rate limit exceeded
        if len(requests) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f'Rate limit exceeded for IP: {ip}')
            return HttpResponse('Rate limit exceeded. Please try again later.', status=429)

        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, settings.RATE_LIMIT_WINDOW)

        response = self.get_response(request)
        return response

class SecurityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log suspicious activities
        suspicious_patterns = [
            'union select', 'script', 'javascript:', 'onload=', 'onerror=',
            '<script', '</script>', 'eval(', 'alert(', 'document.cookie'
        ]

        # Check query parameters and POST data
        query_string = request.META.get('QUERY_STRING', '').lower()
        if request.method == 'POST':
            post_data = str(request.POST).lower()
        else:
            post_data = ''

        for pattern in suspicious_patterns:
            if pattern in query_string or pattern in post_data:
                logger.warning(f'Suspicious request detected from IP {request.META.get("REMOTE_ADDR")}: {request.path}')
                break

        response = self.get_response(request)

        # Log failed authentication attempts
        if response.status_code == 401 or response.status_code == 403:
            logger.warning(f'Authentication failure from IP {request.META.get("REMOTE_ADDR")}: {request.path}')

        return response

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set language from session if available
        if hasattr(request, 'session') and 'django_language' in request.session:
            from django.utils import translation
            translation.activate(request.session['django_language'])

        response = self.get_response(request)
        return response
