"""
Custom Exception Classes and Handler for ScholarPulse API.

Provides structured error responses with error codes, messages,
and optional retry guidance.
"""
import logging
from datetime import datetime
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status

logger = logging.getLogger(__name__)


class ScholarPulseException(APIException):
    """Base exception for ScholarPulse API errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'INTERNAL_ERROR'
    default_detail = 'An unexpected error occurred.'
    retry_after = None
    
    def __init__(self, detail=None, code=None, retry_after=None):
        super().__init__(detail=detail, code=code)
        self.retry_after = retry_after


class ValidationError(ScholarPulseException):
    """Raised when request validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'VALIDATION_ERROR'
    default_detail = 'Invalid request parameters.'


class TaskNotFoundError(ScholarPulseException):
    """Raised when a task ID is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'TASK_NOT_FOUND'
    default_detail = 'The requested task was not found.'


class TaskAlreadyCompletedError(ScholarPulseException):
    """Raised when trying to cancel a completed task."""
    status_code = status.HTTP_409_CONFLICT
    default_code = 'TASK_ALREADY_COMPLETED'
    default_detail = 'Cannot cancel a task that has already completed.'


class LLMServiceError(ScholarPulseException):
    """Raised when LLM service fails."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'LLM_SERVICE_ERROR'
    default_detail = 'AI service is temporarily unavailable.'
    
    def __init__(self, detail=None, retry_after=30):
        super().__init__(detail=detail, retry_after=retry_after)


class LLMRateLimitError(ScholarPulseException):
    """Raised when LLM rate limit is hit."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = 'RATE_LIMIT_EXCEEDED'
    default_detail = 'Too many requests. Please wait before trying again.'
    
    def __init__(self, detail=None, retry_after=60):
        super().__init__(detail=detail, retry_after=retry_after)


class SearchServiceError(ScholarPulseException):
    """Raised when paper search fails."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = 'SEARCH_SERVICE_ERROR'
    default_detail = 'Could not fetch papers from external sources.'


class TaskTimeoutError(ScholarPulseException):
    """Raised when a task times out."""
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_code = 'TASK_TIMEOUT'
    default_detail = 'The research task took too long to complete.'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns structured error responses.
    
    Response format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {...},
            "timestamp": "2026-02-07T13:27:41Z",
            "retry_after": 30  // optional
        }
    }
    """
    # Get the standard DRF response first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Extract error details
        if isinstance(exc, ScholarPulseException):
            code = exc.default_code
            message = str(exc.detail) if exc.detail else exc.default_detail
            retry_after = exc.retry_after
        else:
            code = getattr(exc, 'default_code', 'API_ERROR')
            message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
            retry_after = None
        
        # Build structured error response
        error_data = {
            'error': {
                'code': code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
            }
        }
        
        # Add details if available
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_data['error']['details'] = exc.detail
        
        # Add retry_after if applicable
        if retry_after:
            error_data['error']['retry_after'] = retry_after
            response['Retry-After'] = str(retry_after)
        
        response.data = error_data
        
        # Log the error
        logger.error(
            f"API Error: {code} - {message}",
            extra={
                'view': context.get('view').__class__.__name__ if context.get('view') else None,
                'request_path': context.get('request').path if context.get('request') else None,
                'status_code': response.status_code,
            }
        )
    
    return response
