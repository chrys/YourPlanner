from django.utils.deprecation import MiddlewareMixin
import re
from django.http import HttpResponseForbidden
from django.conf import settings

class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance security by preventing common attack patterns.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for SQL injection detection
        self.sql_patterns = re.compile(
            r'(\b(select|update|insert|delete|drop|alter|union|exec|declare)\b)|(-{2})|(/\*)', 
            re.IGNORECASE
        )
        # Compile regex patterns for XSS detection
        self.xss_patterns = re.compile(
            r'(<script|javascript:|on\w+\s*=|alert\(|eval\(|\bdata:)', 
            re.IGNORECASE
        )
        
    def process_request(self, request):
        # Check for SQL injection attempts in GET parameters
        for key, value in request.GET.items():
            if isinstance(value, str) and self.sql_patterns.search(value):
                return HttpResponseForbidden("Forbidden: Potential security threat detected")
                
        # Check for XSS attempts in GET parameters
        for key, value in request.GET.items():
            if isinstance(value, str) and self.xss_patterns.search(value):
                return HttpResponseForbidden("Forbidden: Potential security threat detected")
                
        return None
        
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Add Content-Security-Policy header in production
        if not settings.DEBUG:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' https://cdn.jsdelivr.net",
                "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "base-uri 'self'",
                "object-src 'none'"
            ]
            response['Content-Security-Policy'] = "; ".join(csp_directives)
            
        return response

