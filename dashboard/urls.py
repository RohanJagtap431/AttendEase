from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    path('manage-teachers/', views.manage_teachers, name='manage_teachers'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    
    path(
        'edit-teacher/<int:teacher_id>/',
        views.edit_teacher,
        name='edit_teacher'
    ),

    path(
        'toggle-teacher-status/<int:teacher_id>/',
        views.toggle_teacher_status,
        name='toggle_teacher_status'
    ),
    
    path(
        'delete-teacher/<int:teacher_id>/',
        views.delete_teacher,
        name='delete_teacher'
    ),
    
    path('manage-students/', views.manage_students, name='manage_students'),
    
    path(
        'edit-student/<int:student_id>/',
        views.edit_student,
        name='edit_student'
    ),

    path(
        'toggle-student-status/<int:student_id>/',
        views.toggle_student_status,
        name='toggle_student_status'
    ),

    path(
        'delete-student/<int:student_id>/',
        views.delete_student,
        name='delete_student'
    ),
    
    path('add-student/', views.add_student, name='add_student'),
    
    
    # Classroom Management
    path(
        'manage-classrooms/',
        views.manage_classrooms,
        name='manage_classrooms'
    ),

    path(
        'add-classroom/',
        views.add_classroom,
        name='add_classroom'
    ),

    path(
        'edit-classroom/<int:classroom_id>/',
        views.edit_classroom,
        name='edit_classroom'
    ),

    path(
        'delete-classroom/<int:classroom_id>/',
        views.delete_classroom,
        name='delete_classroom'
    ),
    
    
    path('manage-subjects/', views.manage_subjects, name='manage_subjects'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('edit-subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    
    
    path('manage-assignments/', views.manage_assignments, name='manage_assignments'),
    path('add-assignment/', views.add_assignment, name='add_assignment'),
    path('edit-assignment/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('delete-assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),

    
    path('system-overview/', views.system_overview, name='system_overview'),
    
    path(
        'my-assignments/',
        views.teacher_assignments,
        name='teacher_assignments'
    ),
    
    path('student/', views.student_dashboard, name='student_dashboard'),

    path('student/profile/', views.student_profile, name='student_profile'),
]