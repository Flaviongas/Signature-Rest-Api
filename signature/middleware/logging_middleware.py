from signature.serializers import MajorSerializer, StudentSerializer, SubjectSerializer, UserSerializer
from django.utils.deprecation import MiddlewareMixin
from colorama import Fore, Style, init
import logging
import json
import time
import re


logger = logging.getLogger('api') #Logger configuration
init() #Colorama initialization

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
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Obtener información básica del usuario
        user_info = {
            'username': 'anonymous',
            'is_admin': False
        }
        
        if request.user.is_authenticated:
            user_info.update({
                'username': str(request.user),
                'is_admin': request.user.is_staff or request.user.is_superuser
            })
        
        # Detectar operaciones CRUD relevantes
        operation_log = self.get_operation_details(request, response)

        # Construir mensaje principal
        log_message = (
            f"{self.color_method(request.method)} {request.path} - "
            f"{self.color_status(response.status_code)} "
            f"User: {Fore.BLUE}{user_info['username']}{Style.RESET_ALL} "
            f"({duration:.2f}s) "
            f"({'Admin' if user_info['is_admin'] else 'User'})"
        )
        
        # Nivel de log basado en status code
        log_level = self.get_log_level(response.status_code)
        self.color_level(log_level)
        # Registrar mensaje principal
        logger.log(log_level, log_message)
        
        # Registrar detalles específicos de operación si existen
        if operation_log:
            logger.info(f"Operation: {operation_log}")
        
        return response

    def get_operation_details(self, request, response):
        """Detecta y formatea operaciones específicas en los modelos clave"""

        operation_map = {
            'GET': 'Retrieved',
            'POST': 'Created',
            'PUT': 'Updated',
            'PATCH': 'Updated',
            'DELETE': 'Deleted'
        }
        
        # Detectar modelo afectado
        model_match = {
            '/api/subjects/': 'Subject',
            '/api/students/': 'Student',
            '/api/majors/': 'Major',
            '/api/users/': 'User'
        }
        
        if request.method in ["GET"]:
            for path, model in model_match.items():
                if request.path.startswith(path):
                    operation = operation_map.get(request.method)
                    return f"{operation} {model} "
        else:
            for path, model in model_match.items():
                if request.path.startswith(path):
                    operation = operation_map.get(request.method)
                    resource_name = self.get_resource_name(request, response)
                    return f"{operation} {model} {resource_name}"

        return None 

    def get_resource_name(self, request, response):
        """
        Obtiene un nombre o identificador de un recurso para registrar en logs
        """
        preferred_keys = ['username', 'name', 'first_name']

        # Usar el nombre guardado si existe
        if 'RESOURCE_NAME' in request.META:
            return str(request.META['RESOURCE_NAME'])
        
        try:
            if isinstance(response.data, dict):
                for key in preferred_keys:
                    if key in response.data:
                        return str(response.data[key])
                return f"[Data: {str(response.data)[:50]}...]"
            else:
                return f"[{type(response.data).__name__} Data]"
        except Exception as e:
            logger.warning(f"Error retrieving resource name: {str(e)}")
            return "[error retrieving]"


    def get_instance_data(self, response, serializer_class):
        """
        Extrae y sanitiza datos de la respuesta
        """
        try:
            if response.status_code in [200, 201]:
                serializer = serializer_class(data=response.data)
                serializer.is_valid()
                return self.sanitize_data(serializer.validated_data)
        except Exception as e:
            logger.warning(f"Error parsing response data: {str(e)}")
            
    
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
            return logging.WARNING if status_code not in [404] else logging.INFO
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
    
    def color_level(self, level):
        """Applies colors based on the log level"""
        if level >= logging.ERROR:
            return Fore.RED
        elif level >= logging.WARNING:
            return Fore.YELLOW
        return Fore.GREEN
    
    def color_status(self, status_code):
        """Applies colors based on the status code"""
        if status_code >= 500:
            return f"{Fore.RED}{status_code}{Style.RESET_ALL}"
        elif status_code >= 400:
            return f"{Fore.YELLOW}{status_code}{Style.RESET_ALL}"
        elif status_code >= 300:
            return f"{Fore.CYAN}{status_code}{Style.RESET_ALL}"
        return f"{Fore.GREEN}{status_code}{Style.RESET_ALL}"