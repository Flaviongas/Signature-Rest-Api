from django.utils.deprecation import MiddlewareMixin
from colorama import Fore, Back, Style
import logging
import json
import time
import re

logger = logging.getLogger('api')

# Words sensitive to reject
SENSITIVE_KEYS = {'password', 'token', 'authorization', 'auth', 'credentials'}
SENSITIVE_PATTERNS = [
    re.compile(r'(\b|_)(password|token|auth)(\b|_)', re.IGNORECASE),
    re.compile(r'bearer\s+\w+', re.IGNORECASE)
]

class RequestLoggingMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.sensitive_keys = SENSITIVE_KEYS
        self.sensitive_patterns = SENSITIVE_PATTERNS
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        duration = time.time() - request.start_time
        
        # Obtain user data
        request_data = {
            'user': str(request.user),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': f"{duration:.2f}s",
            'client_ip': self.get_client_ip(request),
            'query_params': self.sanitize_data(dict(request.GET)),
            'request_body': self.sanitize_data(self.parse_body(request)),
        }
        
        # Determine log level based on status code
        log_level = self.get_log_level(response.status_code)
        
        # Modify the log message with colors
        colored_method = self.color_method(request.method)
        colored_status = self.color_status(response.status_code)
        
        log_message = (
            f"{colored_method} {request.path} - {colored_status} "
            f"(User: {Fore.BLUE}{request_data['user']}{Style.RESET_ALL}, "
            f"IP: {Fore.MAGENTA}{request_data['client_ip']}{Style.RESET_ALL}, "
            f"Duration: {Fore.CYAN}{request_data['duration']}{Style.RESET_ALL})"
        )
        
        # Register the log message
        logger.log(log_level, log_message)
        
        # Log the request details
        logger.debug(f"Request details: {request_data}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def parse_body(self, request):
        """Try to parse the request body based on content type"""
        try:
            if request.body:
                if 'application/json' in request.content_type:
                    return json.loads(request.body.decode('utf-8'))
                elif 'form-data' in request.content_type or 'urlencoded' in request.content_type:
                    return dict(request.POST)
                return request.body.decode('utf-8')[:500]  # Limit size
            return None
        except Exception:
            return str(request.body)[:500]
    
    def sanitize_data(self, data):
        """Filters sensitive data from the request"""
        if isinstance(data, dict):
            return {k: self.redact_sensitive(k, v) for k, v in data.items()}
        elif isinstance(data, str):
            return self.redact_string(data)
        elif isinstance(data, (list, tuple)):
            return [self.sanitize_data(item) for item in data]
        return data
    
    def redact_sensitive(self, key, value):
        """Redact sensitive keys and values"""
        key_str = str(key).lower()
        if any(sensitive in key_str for sensitive in self.sensitive_keys):
            return '[REDACTED]'
        return self.sanitize_data(value)
    
    def redact_string(self, text):
        """Redact sensitive patterns in strings"""
        text = str(text)
        for pattern in self.sensitive_patterns:
            text = pattern.sub('[REDACTED]', text)
        return text
    
    def get_log_level(self, status_code):
        """Determines the log level based on the status code"""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        return logging.INFO
    
    def color_method(self, method):
        """Applies colors based on the HTTP method"""
        colors = {
            'GET': Fore.GREEN,
            'POST': Fore.BLUE,
            'PUT': Fore.YELLOW,
            'PATCH': Fore.YELLOW,
            'DELETE': Fore.RED,
        }
        return f"{colors.get(method, Fore.WHITE)}{method}{Style.RESET_ALL}"
    
    def color_status(self, status_code):
        """Applies colors based on the status code"""
        if status_code >= 500:
            return f"{Fore.RED}{status_code}{Style.RESET_ALL}"
        elif status_code >= 400:
            return f"{Fore.YELLOW}{status_code}{Style.RESET_ALL}"
        elif status_code >= 300:
            return f"{Fore.CYAN}{status_code}{Style.RESET_ALL}"
        return f"{Fore.GREEN}{status_code}{Style.RESET_ALL}"