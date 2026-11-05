from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'assignment',
        'date',
        'status',
        'marked_by',
    )

    list_filter = (
        'status',
        'date',
        'assignment__subject',
        'assignment__classroom',
    )

    search_fields = (
        'student__user__username',
        'student__roll_number',
        'assignment__subject__name',
    )

    date_hierarchy = 'date'
    ordering = ('-date',)