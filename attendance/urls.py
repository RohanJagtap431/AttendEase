from django.urls import path
from . import views

urlpatterns = [
    path(
        'mark/<int:assignment_id>/',
        views.mark_attendance,
        name='mark_attendance'
    ),
    
    path(
        'report/<int:assignment_id>/',
        views.attendance_report,
        name='attendance_report'
    ),
    
    path(
        'export/excel/<int:assignment_id>/',
        views.export_attendance_excel,
        name='export_attendance_excel'
    ),
    
    path(
        'export/pdf/<int:assignment_id>/',
        views.export_attendance_pdf,
        name='export_attendance_pdf'
    ),
    
    path(
        'student-report/<int:assignment_id>/<int:student_id>/',
        views.student_attendance_report,
        name='student_attendance_report'
    ),
    
    
    path(
        'admin-monitor/',
        views.admin_attendance_monitor,
        name='admin_attendance_monitor'
    ),
    
    path(
        'teacher-records/',
        views.teacher_attendance_records,
        name='teacher_attendance_records'
    ),
    
    path(
        'student/my-attendance/',
        views.student_my_attendance,
        name='student_my_attendance'
    ),

]