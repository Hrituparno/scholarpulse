"""
API Views for ScholarPulse REST endpoints.

Implements:
- Research task submission
- Task status polling
- Result retrieval
- Task cancellation
- Error logging
- Health check
"""
import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (
    ResearchSubmitSerializer,
    ResearchSubmitResponseSerializer,
    TaskStatusSerializer,
    ResearchResultSerializer,
    ResearchListSerializer,
    ErrorLogSerializer,
)
from .exceptions import (
    ValidationError,
    TaskNotFoundError,
    TaskAlreadyCompletedError,
)
from research.models import ResearchTask, ErrorLog
from research.services import AgentService

logger = logging.getLogger(__name__)


class ResearchSubmitView(APIView):
    """
    POST /api/research/submit/
    
    Submit a new research task for execution.
    Returns task_id for status polling.
    """
    
    def post(self, request):
        serializer = ResearchSubmitSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise ValidationError(detail=serializer.errors)
        
        validated_data = serializer.validated_data
        
        # Create task record
        task = ResearchTask.objects.create(
            input_params={
                'query': validated_data['query'],
                'mode': validated_data['mode'],
                'year_filter': validated_data.get('year_filter'),
                'llm_provider': validated_data['llm_provider'],
            }
        )
        
        logger.info(f"Created research task {task.id} for query: {validated_data['query'][:50]}")
        
        # Execute research synchronously for MVP
        # In production, this should be a Celery task
        try:
            service = AgentService(task_id=str(task.id))
            service.execute(task)
        except Exception as e:
            logger.error(f"Task {task.id} failed during execution: {e}", exc_info=True)
            task.mark_failed(
                error_code='EXECUTION_ERROR',
                error_message=str(e)
            )
        
        # Return response
        response_data = {
            'task_id': task.id,
            'status': task.status,
            'message': 'Research task submitted successfully' if task.status != 'FAILED' else 'Task failed during execution'
        }
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if task.status != 'FAILED' else status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ResearchStatusView(APIView):
    """
    GET /api/research/status/<task_id>/
    
    Poll the status of a research task.
    """
    
    def get(self, request, task_id):
        try:
            task = ResearchTask.objects.get(id=task_id)
        except ResearchTask.DoesNotExist:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        response_data = {
            'task_id': task.id,
            'status': task.status,
            'progress': task.progress,
            'current_step': task.current_step,
            'started_at': task.started_at,
            'completed_at': task.completed_at,
            'error': task.error_data,
        }
        
        return Response(response_data)


class ResearchResultView(APIView):
    """
    GET /api/research/result/<task_id>/
    
    Retrieve the results of a completed research task.
    """
    
    def get(self, request, task_id):
        try:
            task = ResearchTask.objects.get(id=task_id)
        except ResearchTask.DoesNotExist:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        if task.status == ResearchTask.Status.PENDING:
            return Response(
                {'message': 'Task is still pending', 'status': task.status},
                status=status.HTTP_202_ACCEPTED
            )
        
        if task.status == ResearchTask.Status.RUNNING:
            return Response(
                {
                    'message': 'Task is still running',
                    'status': task.status,
                    'progress': task.progress,
                    'current_step': task.current_step
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        if task.status == ResearchTask.Status.FAILED:
            return Response(
                {
                    'message': 'Task failed',
                    'status': task.status,
                    'error': task.error_data
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if task.status == ResearchTask.Status.CANCELLED:
            return Response(
                {'message': 'Task was cancelled', 'status': task.status},
                status=status.HTTP_410_GONE
            )
        
        # Task completed - return results
        output = task.output_data or {}
        response_data = {
            'task_id': task.id,
            'query': task.input_params.get('query', ''),
            'papers': output.get('papers', []),
            'ideas': output.get('ideas', []),
            'report_sections': output.get('report_sections', {}),
            'report_formats': output.get('report_formats', {}),
            'generated_at': task.completed_at,
        }
        
        return Response(response_data)


class ResearchCancelView(APIView):
    """
    POST /api/research/cancel/<task_id>/
    
    Cancel a running or pending research task.
    """
    
    def post(self, request, task_id):
        try:
            task = ResearchTask.objects.get(id=task_id)
        except ResearchTask.DoesNotExist:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        if task.status in [ResearchTask.Status.COMPLETED, ResearchTask.Status.FAILED]:
            raise TaskAlreadyCompletedError(
                f"Cannot cancel task in {task.status} state"
            )
        
        if task.status == ResearchTask.Status.CANCELLED:
            return Response(
                {'message': 'Task already cancelled', 'task_id': task.id},
                status=status.HTTP_200_OK
            )
        
        task.mark_cancelled()
        logger.info(f"Task {task_id} cancelled")
        
        return Response(
            {'message': 'Task cancelled successfully', 'task_id': task.id},
            status=status.HTTP_200_OK
        )


class ErrorLogView(APIView):
    """
    POST /api/errors/log/
    
    Log errors from the frontend for centralized tracking.
    """
    
    def post(self, request):
        serializer = ErrorLogSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'message': 'Invalid error log data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Create error log
        error_log = ErrorLog.objects.create(
            source=ErrorLog.Source.FRONTEND,
            error_code=validated_data['error_code'],
            message=validated_data['message'],
            context=validated_data.get('context'),
            stack_trace=validated_data.get('stack_trace', ''),
            user_agent=validated_data.get('user_agent', ''),
            ip_address=ip_address,
        )
        
        logger.warning(
            f"Frontend error logged: {validated_data['error_code']} - {validated_data['message'][:100]}"
        )
        
        return Response(
            {'message': 'Error logged successfully', 'log_id': str(error_log.id)},
            status=status.HTTP_201_CREATED
        )


class ResearchListView(APIView):
    """
    GET /api/research/list/
    
    List all research tasks.
    """
    
    def get(self, request):
        tasks = ResearchTask.objects.all().order_by('-created_at')
        serializer = ResearchListSerializer(tasks, many=True)
        return Response(serializer.data)


class ResearchStatsView(APIView):
    """
    GET /api/research/stats/
    
    Get aggregated research statistics.
    """
    
    def get(self, request):
        completed_tasks = ResearchTask.objects.filter(status=ResearchTask.Status.COMPLETED)
        
        total_papers = 0
        for task in completed_tasks:
            if task.output_data and 'papers' in task.output_data:
                total_papers += len(task.output_data['papers'])
        
        return Response({
            'total_papers': total_papers,
            'total_searches': ResearchTask.objects.count(),
            'total_reports': completed_tasks.count(),
        })


class HealthCheckView(APIView):
    """
    GET /api/health/
    
    Simple health check endpoint.
    """
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'ScholarPulse API',
            'timestamp': timezone.now().isoformat()
        })
