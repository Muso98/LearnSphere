from django.contrib import admin
from .models import Attendance, Grade, GradeAudit

admin.site.register(Attendance)
admin.site.register(Grade)

@admin.register(GradeAudit)
class GradeAuditAdmin(admin.ModelAdmin):
    list_display = ('grade', 'action', 'changed_by', 'previous_value', 'new_value', 'timestamp')
    list_filter = ('action', 'timestamp', 'changed_by')
    search_fields = ('grade__student__username', 'grade__subject__name')

