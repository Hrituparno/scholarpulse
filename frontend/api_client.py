"""
ScholarPulse API Client for Streamlit Frontend.

Provides retry-safe REST API calls with structured error handling.
"""
import time
import logging
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


@dataclass
class APIError:
    """Structured API error."""
    code: str
    message: str
    details: Optional[Dict] = None
    retry_after: Optional[int] = None
    
    @classmethod
    def from_response(cls, response: requests.Response) -> 'APIError':
        """Create APIError from response."""
        try:
            data = response.json()
            if 'error' in data:
                err = data['error']
                return cls(
                    code=err.get('code', 'UNKNOWN_ERROR'),
                    message=err.get('message', 'An error occurred'),
                    details=err.get('details'),
                    retry_after=err.get('retry_after')
                )
        except:
            pass
        return cls(
            code='HTTP_ERROR',
            message=f"HTTP {response.status_code}: {response.reason}"
        )


class ScholarPulseAPI:
    """
    REST API client for ScholarPulse backend.
    
    Features:
    - Automatic retry on transient failures
    - Structured error handling
    - Connection pooling via requests.Session
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        self.max_retries = 3
        self.retry_delay = 1.5
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, timeout=60, **kwargs)
                
                # Success or client error (no retry)
                if response.status_code < 500:
                    return response
                
                # Server error - retry
                last_error = APIError.from_response(response)
                logger.warning(f"Server error (attempt {attempt + 1}): {last_error.message}")
                
            except requests.exceptions.ConnectionError as e:
                last_error = APIError(
                    code='CONNECTION_ERROR',
                    message='Could not connect to backend server'
                )
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                
            except requests.exceptions.Timeout as e:
                last_error = APIError(
                    code='TIMEOUT_ERROR',
                    message='Request timed out'
                )
                logger.warning(f"Timeout (attempt {attempt + 1}): {e}")
                
            except requests.exceptions.RequestException as e:
                last_error = APIError(
                    code='REQUEST_ERROR',
                    message=str(e)
                )
                logger.warning(f"Request error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (2 ** attempt))
        
        raise APIException(last_error)
    
    def health_check(self) -> bool:
        """Check if backend is healthy."""
        try:
            response = self._request('GET', '/api/health/')
            return response.status_code == 200
        except:
            return False
    
    def submit_research(
        self,
        query: str,
        mode: str = 'Deep Research',
        year_filter: Optional[int] = None,
        llm_provider: str = 'groq'
    ) -> str:
        """
        Submit a new research task.
        
        Returns:
            task_id (str): UUID of the created task
            
        Raises:
            APIException: If submission fails
        """
        payload = {
            'query': query,
            'mode': mode,
            'llm_provider': llm_provider,
        }
        if year_filter and year_filter > 0:
            payload['year_filter'] = year_filter
        
        response = self._request('POST', '/api/research/submit/', json=payload)
        
        if response.status_code == 201:
            return response.json()['task_id']
        elif response.status_code == 500:
            # Task was created but failed during execution
            data = response.json()
            return data.get('task_id')
        else:
            raise APIException(APIError.from_response(response))
    
    def list_tasks(self) -> list:
        """
        List all research tasks.
        
        Returns:
            list of dicts with task metadata
        """
        response = self._request('GET', '/api/research/list/')
        if response.status_code == 200:
            return response.json()
        else:
            raise APIException(APIError.from_response(response))
    
    def get_stats(self) -> dict:
        """
        Get aggregated research statistics.
        
        Returns:
            dict with total_papers, total_searches, total_reports
        """
        response = self._request('GET', '/api/research/stats/')
        if response.status_code == 200:
            return response.json()
        else:
            raise APIException(APIError.from_response(response))
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a research task.
        
        Returns:
            dict with status, progress, current_step, error
        """
        response = self._request('GET', f'/api/research/status/{task_id}/')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise APIException(APIError.from_response(response))
    
    def get_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed research task.
        
        Returns:
            dict with papers, ideas, report_sections, report_formats
        """
        response = self._request('GET', f'/api/research/result/{task_id}/')
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            # Still processing
            return response.json()
        else:
            raise APIException(APIError.from_response(response))
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        response = self._request('POST', f'/api/research/cancel/{task_id}/')
        return response.status_code == 200
    
    def log_error(
        self,
        error_code: str,
        message: str,
        context: Optional[Dict] = None,
        stack_trace: Optional[str] = None
    ) -> None:
        """Log an error from the frontend."""
        try:
            self._request('POST', '/api/errors/log/', json={
                'error_code': error_code,
                'message': message,
                'context': context or {},
                'stack_trace': stack_trace or '',
            })
        except:
            # Don't fail on error logging
            logger.error(f"Failed to log error: {error_code} - {message}")
    
    def poll_until_complete(
        self,
        task_id: str,
        on_progress: Optional[callable] = None,
        poll_interval: float = 2.0,
        max_wait: float = 600.0
    ) -> Dict[str, Any]:
        """
        Poll task status until completion.
        
        Args:
            task_id: Task UUID
            on_progress: Callback(progress: int, step: str)
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait
            
        Returns:
            Final result dict
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_data = self.get_status(task_id)
            status = status_data.get('status')
            
            if on_progress:
                on_progress(
                    status_data.get('progress', 0),
                    status_data.get('current_step', '')
                )
            
            if status == TaskStatus.COMPLETED.value:
                return self.get_result(task_id)
            
            if status == TaskStatus.FAILED.value:
                raise APIException(APIError(
                    code=status_data.get('error', {}).get('code', 'TASK_FAILED'),
                    message=status_data.get('error', {}).get('message', 'Task failed')
                ))
            
            if status == TaskStatus.CANCELLED.value:
                raise APIException(APIError(
                    code='TASK_CANCELLED',
                    message='Task was cancelled'
                ))
            
            time.sleep(poll_interval)
        
        raise APIException(APIError(
            code='POLL_TIMEOUT',
            message='Task did not complete within the expected time'
        ))


class APIException(Exception):
    """Exception raised for API errors."""
    
    def __init__(self, error: APIError):
        self.error = error
        super().__init__(error.message)
    
    @property
    def code(self) -> str:
        return self.error.code
    
    @property
    def is_retryable(self) -> bool:
        return self.error.code in [
            'CONNECTION_ERROR',
            'TIMEOUT_ERROR',
            'LLM_SERVICE_ERROR',
            'SEARCH_SERVICE_ERROR',
        ]
