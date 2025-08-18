"""
Custom middleware for PMCELL catalog
"""

import time
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings


class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429


class SecurityMiddleware:
    """
    Custom security middleware for additional headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
            
        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware for API endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limit settings (requests per minute)
        self.limits = {
            '/api/liberate-prices/': 5,     # 5 requests per minute
            '/api/track-journey/': 60,      # 60 requests per minute
            '/api/track-abandoned-cart/': 3, # 3 requests per minute
            '/api/search-suggestions/': 30,  # 30 requests per minute
        }

    def __call__(self, request):
        # Check if this is an API endpoint we want to rate limit
        path = request.path
        if any(path.startswith(api_path) for api_path in self.limits.keys()):
            if self.is_rate_limited(request):
                return HttpResponseTooManyRequests("Rate limit exceeded. Please try again later.")
        
        response = self.get_response(request)
        return response

    def is_rate_limited(self, request):
        """
        Check if the request should be rate limited
        """
        # Get client IP
        ip = self.get_client_ip(request)
        path = request.path
        
        # Find matching rate limit
        limit = None
        for api_path, rate_limit in self.limits.items():
            if path.startswith(api_path):
                limit = rate_limit
                break
        
        if limit is None:
            return False
        
        # Cache key for this IP and endpoint
        cache_key = f"rate_limit_{ip}_{path}"
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return True
        
        # Increment count with 60-second expiry
        cache.set(cache_key, current_count + 1, 60)
        return False

    def get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIThrottleMiddleware:
    """
    Additional throttling for webhook endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.webhook_endpoints = [
            '/api/liberate-prices/',
            '/api/track-abandoned-cart/',
        ]

    def __call__(self, request):
        # Apply additional throttling to webhook endpoints
        if request.path in self.webhook_endpoints:
            if self.is_webhook_throttled(request):
                return HttpResponseTooManyRequests("Webhook throttle limit exceeded.")
        
        response = self.get_response(request)
        return response

    def is_webhook_throttled(self, request):
        """
        More restrictive throttling for webhook endpoints
        """
        ip = self.get_client_ip(request)
        path = request.path
        
        # Very restrictive: 1 request per 5 seconds for webhooks
        cache_key = f"webhook_throttle_{ip}_{path}"
        
        if cache.get(cache_key):
            return True
        
        # Set throttle for 5 seconds
        cache.set(cache_key, True, 5)
        return False

    def get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip