"""
Database Models for ScholarPulse Research Tasks.

Minimal schema designed for easy PostgreSQL migration:
- Uses Django ORM only (no raw SQL)
- Uses JSONField for flexible data storage
- All fields use database-agnostic types
"""
import uuid
from django.db import models
from django.utils import timezone


class ResearchTask(models.Model):
    """
    Tracks research task execution state and results.
    
    Designed for easy PostgreSQL migration:
    - UUID primary key (works with both SQLite and PostgreSQL)
    - JSONField for flexible nested data (SQLite uses TEXT, PostgreSQL uses native JSONB)
    - DateTimeField with timezone awareness
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    # Primary key - UUID for distributed safety
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Task status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    progress = models.IntegerField(default=0)
    current_step = models.CharField(max_length=200, blank=True, default='')
    
    # Input parameters (stored as JSON for flexibility)
    input_params = models.JSONField(
        default=dict,
        help_text="Research parameters: query, mode, year_filter, llm_provider"
    )
    
    # Output results (stored as JSON)
    output_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Research results: papers, ideas, report_sections, report_formats"
    )
    
    # Error information
    error_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Error details if task failed: code, message, traceback"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Research Task'
        verbose_name_plural = 'Research Tasks'
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        query = self.input_params.get('query', 'Unknown')[:50]
        return f"{self.id} - {query} ({self.status})"
    
    def mark_running(self):
        """Mark task as running."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])
    
    def mark_completed(self, output_data: dict):
        """Mark task as completed with results."""
        self.status = self.Status.COMPLETED
        self.progress = 100
        self.output_data = output_data
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'progress', 'output_data', 'completed_at', 'updated_at'])
    
    def mark_failed(self, error_code: str, error_message: str, traceback: str = None):
        """Mark task as failed with error details."""
        self.status = self.Status.FAILED
        self.error_data = {
            'code': error_code,
            'message': error_message,
            'traceback': traceback,
            'failed_at': timezone.now().isoformat()
        }
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_data', 'completed_at', 'updated_at'])
    
    def mark_cancelled(self):
        """Mark task as cancelled."""
        self.status = self.Status.CANCELLED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def update_progress(self, progress: int, current_step: str = None):
        """Update task progress."""
        self.progress = min(max(progress, 0), 100)
        if current_step:
            self.current_step = current_step
        self.save(update_fields=['progress', 'current_step', 'updated_at'])


class ErrorLog(models.Model):
    """
    Centralized error logging for debugging and monitoring.
    """
    
    class Source(models.TextChoices):
        FRONTEND = 'FRONTEND', 'Frontend'
        BACKEND = 'BACKEND', 'Backend'
        LLM = 'LLM', 'LLM Service'
        SEARCH = 'SEARCH', 'Search Service'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Error identification
    source = models.CharField(max_length=20, choices=Source.choices, db_index=True)
    error_code = models.CharField(max_length=50, db_index=True)
    message = models.TextField()
    
    # Context
    context = models.JSONField(null=True, blank=True)
    stack_trace = models.TextField(blank=True, default='')
    
    # Related task (optional)
    task = models.ForeignKey(
        ResearchTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_logs'
    )
    
    # Metadata
    user_agent = models.CharField(max_length=500, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'
    
    def __str__(self):
        return f"[{self.source}] {self.error_code}: {self.message[:50]}"
