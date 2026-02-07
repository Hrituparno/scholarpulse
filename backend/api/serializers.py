"""
Request/Response Serializers for ScholarPulse API.

These serializers define the contract between frontend and backend,
ensuring consistent data validation and documentation.
"""
from rest_framework import serializers


class ResearchSubmitSerializer(serializers.Serializer):
    """Request schema for submitting a new research task."""
    
    query = serializers.CharField(
        max_length=500,
        required=True,
        help_text="Research query or topic to investigate"
    )
    mode = serializers.ChoiceField(
        choices=['Deep Research', 'Web Search', 'Study & Learn'],
        default='Deep Research',
        help_text="Research mode determining the search strategy"
    )
    year_filter = serializers.IntegerField(
        min_value=0,
        max_value=2030,
        required=False,
        allow_null=True,
        help_text="Filter papers by year (0 or null = all years)"
    )
    llm_provider = serializers.ChoiceField(
        choices=['groq', 'oxlo', 'gemini'],
        default='groq',
        help_text="LLM provider for analysis"
    )
    
    def validate_query(self, value):
        """Ensure query is not just whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Query cannot be empty or whitespace only")
        return value.strip()


class ResearchSubmitResponseSerializer(serializers.Serializer):
    """Response schema after successful task submission."""
    
    task_id = serializers.UUIDField(help_text="Unique identifier for tracking the task")
    status = serializers.CharField(help_text="Initial task status")
    message = serializers.CharField(help_text="Human-readable status message")


class TaskStatusSerializer(serializers.Serializer):
    """Response schema for task status polling."""
    
    task_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED']
    )
    progress = serializers.IntegerField(min_value=0, max_value=100)
    current_step = serializers.CharField(allow_blank=True)
    started_at = serializers.DateTimeField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    error = serializers.DictField(required=False, allow_null=True)


class PaperSerializer(serializers.Serializer):
    """Schema for a single research paper."""
    
    title = serializers.CharField()
    authors = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    pdf_url = serializers.URLField(allow_blank=True)
    google_scholar_url = serializers.URLField(allow_blank=True)
    objective = serializers.CharField(allow_blank=True)
    method = serializers.CharField(allow_blank=True)
    tools = serializers.CharField(allow_blank=True)
    results = serializers.CharField(allow_blank=True)


class IdeaSerializer(serializers.Serializer):
    """Schema for a generated research idea."""
    
    title = serializers.CharField()
    description = serializers.CharField()
    requirements = serializers.ListField(child=serializers.CharField(), required=False)


class ResearchResultSerializer(serializers.Serializer):
    """Response schema for completed research results."""
    
    task_id = serializers.UUIDField()
    query = serializers.CharField()
    papers = PaperSerializer(many=True)
    ideas = IdeaSerializer(many=True)
    report_sections = serializers.DictField()
    report_formats = serializers.DictField(help_text="URLs/paths to different report formats")
    generated_at = serializers.DateTimeField()


class ErrorLogSerializer(serializers.Serializer):
    """Request schema for logging frontend errors."""
    
    error_code = serializers.CharField(max_length=50)
    message = serializers.CharField(max_length=1000)
    context = serializers.DictField(required=False)
    stack_trace = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)


class ResearchListSerializer(serializers.Serializer):
    """Response schema for listing research tasks."""
    
    task_id = serializers.UUIDField(source='id')
    query = serializers.SerializerMethodField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
    paper_count = serializers.SerializerMethodField()
    idea_count = serializers.SerializerMethodField()
    
    def get_query(self, obj):
        return obj.input_params.get('query', 'Unknown')
    
    def get_paper_count(self, obj):
        if obj.output_data and 'papers' in obj.output_data:
            return len(obj.output_data['papers'])
        return 0
    
    def get_idea_count(self, obj):
        if obj.output_data and 'ideas' in obj.output_data:
            return len(obj.output_data['ideas'])
        return 0


class APIErrorSerializer(serializers.Serializer):
    """Standard error response schema."""
    
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()
    retry_after = serializers.IntegerField(required=False, allow_null=True)
