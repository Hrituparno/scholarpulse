from django.contrib import admin
from .models import ResearchTask, ErrorLog


@admin.register(ResearchTask)
class ResearchTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_query', 'status', 'progress', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'input_params']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_query(self, obj):
        return obj.input_params.get('query', 'N/A')[:50]
    get_query.short_description = 'Query'


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'error_code', 'message_preview', 'created_at']
    list_filter = ['source', 'error_code', 'created_at']
    search_fields = ['error_code', 'message']
    readonly_fields = ['id', 'created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
