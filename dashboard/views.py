
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from students.models import StudentProfile
from attendance.models import Attendance
from django.db.models import Count, Q
from accounts.models import User
from students.models import StudentProfile
from academics.models import (
    ClassRoom,
    Subject,
    TeacherProfile,
    TeacherAssignment,
)
from students.models import StudentProfile
from attendance.models import Attendance


from django.db.models import Count

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from academics.models import TeacherProfile
from django.db import models

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.views.decorators.http import require_POST

from django.db.models.deletion import ProtectedError

from django.utils.dateparse import parse_date

User = get_user_model()

def is_admin(user):
    return user.is_superuser or user.role == 'admin'


def is_teacher(user):
    return user.role == 'teacher'


def is_student(user):
    return user.role == 'student'



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    context = {
        'total_students': StudentProfile.objects.filter(
            user__is_active=True
        ).count(),

        'total_teachers': TeacherProfile.objects.filter(
            user__is_active=True
        ).count(),

        'total_classrooms': ClassRoom.objects.count(),

        'total_subjects': Subject.objects.count(),

        'total_assignments': TeacherAssignment.objects.count(),

        'active_page': 'dashboard',
    }

    return render(
        request,
        'admin/dashboard.html',
        context
    )


@login_required
@user_passes_test(is_admin)
def manage_teachers(request):

    search = request.GET.get('search', '').strip()

    teachers = TeacherProfile.objects.select_related(
        'user'
    ).order_by('user__first_name', 'user__username')

    if search:
        teachers = teachers.filter(
            models.Q(user__username__icontains=search) |
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(employee_id__icontains=search) |
            models.Q(department__icontains=search)
        )

    context = {
        'teachers': teachers,
        'search': search,
        'total_teachers': TeacherProfile.objects.count(),
        'active_page': 'teachers',
    }
    return render(
        request,
        'admin/manage_teachers.html',
        context
    )


@login_required
@user_passes_test(is_admin)
def add_teacher(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        department = request.POST.get('department', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Required field validation
        if not all([
            username, first_name, email,
            employee_id, password, confirm_password
        ]):
            messages.error(request, "Please fill all required fields.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")

        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")

        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists.")

        elif TeacherProfile.objects.filter(employee_id__iexact=employee_id).exists():
            messages.error(request, "Employee ID already exists.")

        else:
            try:
                with transaction.atomic():

                    user = User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        role='teacher',
                        is_active=True,
                    )

                    user.set_password(password)
                    user.save()

                    TeacherProfile.objects.create(
                        user=user,
                        employee_id=employee_id,
                        department=department,
                    )

                messages.success(
                    request,
                    "Teacher account created successfully!"
                )

                return redirect('manage_teachers')

            except IntegrityError:
                messages.error(
                    request,
                    "Could not create teacher. Check username, email and employee ID."
                )

    return render(
        request,
        'admin/add_teacher.html'
    )


@login_required
@user_passes_test(is_admin)
def edit_teacher(request, teacher_id):

    teacher = get_object_or_404(
        TeacherProfile.objects.select_related('user'),
        id=teacher_id
    )

    user = teacher.user

    if request.method == 'POST':

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        department = request.POST.get('department', '').strip()

        if not all([first_name, email, employee_id]):
            messages.error(request, "Please fill all required fields.")

        elif User.objects.filter(
            email__iexact=email
        ).exclude(id=user.id).exists():
            messages.error(request, "Email already exists.")

        elif TeacherProfile.objects.filter(
            employee_id__iexact=employee_id
        ).exclude(id=teacher.id).exists():
            messages.error(request, "Employee ID already exists.")

        else:
            try:
                with transaction.atomic():

                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.phone = phone
                    user.save()

                    teacher.employee_id = employee_id
                    teacher.department = department
                    teacher.save()

                messages.success(
                    request,
                    "Teacher information updated successfully!"
                )

                return redirect('manage_teachers')

            except IntegrityError:
                messages.error(
                    request,
                    "Could not update teacher. Check the entered details."
                )

    context = {
        'teacher': teacher,
    }

    return render(
        request,
        'admin/edit_teacher.html',
        context
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_teacher_status(request, teacher_id):

    teacher = get_object_or_404(
        TeacherProfile.objects.select_related('user'),
        id=teacher_id
    )

    user = teacher.user

    if user.is_superuser or user.role != 'teacher':
        messages.error(request, "This account cannot be changed.")
        return redirect('manage_teachers')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    if user.is_active:
        messages.success(request, "Teacher account activated successfully.")
    else:
        messages.success(request, "Teacher account deactivated successfully.")

    return redirect('manage_teachers')



@login_required
@user_passes_test(is_admin)
@require_POST
def delete_teacher(request, teacher_id):

    teacher = get_object_or_404(
        TeacherProfile.objects.select_related('user'),
        id=teacher_id
    )

    user = teacher.user

    if user.is_superuser or user.role != 'teacher':
        messages.error(request, "This account cannot be deleted.")
        return redirect('manage_teachers')

    teacher_name = user.get_full_name() or user.username

    try:
        with transaction.atomic():
            user.delete()

        messages.success(
            request,
            f"Teacher account '{teacher_name}' deleted successfully."
        )

    except ProtectedError:
        messages.error(
            request,
            "Cannot delete this teacher because attendance records are linked to their assignments. Deactivate the account instead."
        )

    return redirect('manage_teachers')


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):

    # Get assignments of logged-in teacher
    assignments = TeacherAssignment.objects.filter(
        teacher__user=request.user
    ).select_related(
        'classroom',
        'subject'
    ).order_by('classroom__name', 'subject__name')

    # Get attendance records of logged-in teacher
    attendance_records = Attendance.objects.filter(
        assignment__teacher__user=request.user
    )

    # Attendance statistics
    attendance_stats = attendance_records.aggregate(
        total=Count('id'),
        present=Count('id', filter=models.Q(status='present')),
        absent=Count('id', filter=models.Q(status='absent')),
        late=Count('id', filter=models.Q(status='late')),
    )

    # Count unique students in assigned classrooms
    total_students = StudentProfile.objects.filter(
        classroom__teacher_assignments__teacher__user=request.user,
        user__is_active=True
    ).distinct().count()

    # Recent attendance records
    recent_attendance = attendance_records.select_related(
        'student__user',
        'student__classroom',
        'assignment__subject'
    ).order_by('-date', '-created_at')[:5]

    context = {
        'assignments': assignments,
        'total_assignments': assignments.count(),
        'total_students': total_students,
        'attendance_stats': attendance_stats,
        'recent_attendance': recent_attendance,
        'active_page': 'dashboard',
        'active_page': 'attendance',
    }

    return render(
        request,
        'teacher/dashboard.html',
        context
    )


@login_required
@user_passes_test(is_student)
def student_dashboard(request):

    try:
        student = StudentProfile.objects.select_related(
            'user',
            'classroom'
        ).get(user=request.user)

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('login')

    records = Attendance.objects.filter(
        student=student
    ).select_related(
        'assignment__subject',
        'assignment__classroom'
    )

    statistics = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )

    total = statistics['total']
    attended = statistics['present'] + statistics['late']

    percentage = round((attended / total) * 100, 2) if total else 0

    context = {
        'student': student,
        'statistics': statistics,
        'attendance_percentage': percentage,
        'recent_records': records.order_by('-date')[:5],
    }

    return render(request, 'student/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_students(request):

    students = StudentProfile.objects.select_related(
        'user',
        'classroom'
    ).all()

    search = request.GET.get('search', '').strip()

    if search:
        students = students.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(roll_number__icontains=search) |
            models.Q(classroom__name__icontains=search)
        )

    context = {
        'students': students,
        'search': search,
        'total_students': StudentProfile.objects.count(),
        'active_page': 'students',
    }

    return render(
        request,
        'admin/manage_students.html',
        context
    )
    



@login_required
@user_passes_test(is_admin)
def add_student(request):

    classrooms = ClassRoom.objects.all()

    if request.method == 'POST':

        # Personal Information
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        # Academic Information
        roll_number = request.POST.get('roll_number', '').strip()
        classroom_id = request.POST.get('classroom', '')
        admission_date = parse_date(
            request.POST.get('admission_date', '')
        )

        # Parent Information
        parent_name = request.POST.get('parent_name', '').strip()
        parent_phone = request.POST.get('parent_phone', '').strip()

        # Login Credentials
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Required Field Validation
        if not all([
            username,
            first_name,
            email,
            roll_number,
            classroom_id,
            admission_date,
            password,
            confirm_password
        ]):

            messages.error(
                request,
                "Please fill all required fields."
            )

        # Password Validation
        elif password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

        elif len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

        # Username Validation
        elif User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

        # Email Validation
        elif User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

        # Classroom Validation
        elif not ClassRoom.objects.filter(
            id=classroom_id
        ).exists():

            messages.error(
                request,
                "Please select a valid classroom."
            )

        # Roll Number Validation
        elif StudentProfile.objects.filter(
            classroom_id=classroom_id,
            roll_number__iexact=roll_number
        ).exists():

            messages.error(
                request,
                "This roll number already exists in the selected classroom."
            )

        else:

            try:

                with transaction.atomic():

                    # Create Student User
                    user = User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        role='student',
                        is_active=True
                    )

                    user.set_password(password)
                    user.save()

                    # Create Student Profile
                    StudentProfile.objects.create(
                        user=user,
                        roll_number=roll_number,
                        classroom_id=classroom_id,
                        admission_date=admission_date,
                        parent_name=parent_name,
                        parent_phone=parent_phone
                    )

                messages.success(
                    request,
                    f"Student account '{username}' created successfully!"
                )

                return redirect('manage_students')

            except IntegrityError:

                messages.error(
                    request,
                    "Could not create student. Username, email or roll number may already exist."
                )

    context = {
        'classrooms': classrooms,
    }

    return render(
        request,
        'admin/add_student.html',
        context
    )

@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):

    student = get_object_or_404(
        StudentProfile.objects.select_related('user', 'classroom'),
        id=student_id
    )

    user = student.user

    classrooms = ClassRoom.objects.all()

    if request.method == 'POST':

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        roll_number = request.POST.get('roll_number', '').strip()
        classroom_id = request.POST.get('classroom', '')
        admission_date = parse_date(
            request.POST.get('admission_date', '')
        )

        parent_name = request.POST.get('parent_name', '').strip()
        parent_phone = request.POST.get('parent_phone', '').strip()

        if not all([
            first_name,
            email,
            roll_number,
            classroom_id,
            admission_date
        ]):
            messages.error(request, "Please fill all required fields.")

        elif User.objects.filter(
            email__iexact=email
        ).exclude(id=user.id).exists():
            messages.error(request, "Email already exists.")

        elif StudentProfile.objects.filter(
            classroom_id=classroom_id,
            roll_number__iexact=roll_number
        ).exclude(id=student.id).exists():
            messages.error(
                request,
                "This roll number already exists in the selected classroom."
            )

        else:
            try:
                classroom = get_object_or_404(
                    ClassRoom,
                    id=classroom_id
                )

                with transaction.atomic():

                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.phone = phone
                    user.save()

                    student.roll_number = roll_number
                    student.classroom = classroom
                    student.admission_date = admission_date
                    student.parent_name = parent_name
                    student.parent_phone = parent_phone
                    student.save()

                messages.success(
                    request,
                    "Student information updated successfully!"
                )

                return redirect('manage_students')

            except IntegrityError:
                messages.error(
                    request,
                    "Could not update student. Please check the entered details."
                )

    context = {
        'student': student,
        'classrooms': classrooms,
    }

    return render(
        request,
        'admin/edit_student.html',
        context
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_student_status(request, student_id):

    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        id=student_id
    )

    user = student.user

    if user.is_superuser or user.role != 'student':
        messages.error(request, "This account cannot be changed.")
        return redirect('manage_students')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    if user.is_active:
        messages.success(
            request,
            "Student account activated successfully."
        )
    else:
        messages.success(
            request,
            "Student account deactivated successfully."
        )

    return redirect('manage_students')


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_student(request, student_id):

    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        id=student_id
    )

    user = student.user

    if user.is_superuser or user.role != 'student':
        messages.error(request, "This account cannot be deleted.")
        return redirect('manage_students')

    student_name = user.get_full_name() or user.username

    try:
        with transaction.atomic():
            user.delete()

        messages.success(
            request,
            f"Student account '{student_name}' deleted successfully."
        )

    except ProtectedError:
        messages.error(
            request,
            "Cannot delete this student because attendance records are linked to this account. Deactivate the account instead."
        )

    return redirect('manage_students')


@login_required
@user_passes_test(is_admin)
def manage_classrooms(request):

    search = request.GET.get('search', '').strip()

    classrooms = ClassRoom.objects.annotate(
        student_count=Count('students')
    ).order_by('academic_year', 'name', 'section')

    if search:
        classrooms = classrooms.filter(
            models.Q(name__icontains=search) |
            models.Q(section__icontains=search) |
            models.Q(academic_year__icontains=search)
        )

    context = {
        'classrooms': classrooms,
        'search': search,
        'total_classrooms': ClassRoom.objects.count(),
        'active_page': 'classrooms',
    }

    return render(
        request,
        'admin/manage_classrooms.html',
        context
    )


@login_required
@user_passes_test(is_admin)
def add_classroom(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        section = request.POST.get('section', '').strip()
        academic_year = request.POST.get('academic_year', '').strip()

        if not all([name, academic_year]):
            messages.error(
                request,
                "Please fill all required fields."
            )

        elif ClassRoom.objects.filter(
            name__iexact=name,
            section__iexact=section,
            academic_year__iexact=academic_year
        ).exists():
            messages.error(
                request,
                "This classroom already exists for the selected academic year."
            )

        else:
            try:
                ClassRoom.objects.create(
                    name=name,
                    section=section,
                    academic_year=academic_year
                )

                messages.success(
                    request,
                    "Classroom created successfully!"
                )

                return redirect('manage_classrooms')

            except IntegrityError:
                messages.error(
                    request,
                    "Could not create classroom. Please check the details."
                )

    return render(
        request,
        'admin/add_classroom.html'
    )


@login_required
@user_passes_test(is_admin)
def edit_classroom(request, classroom_id):

    classroom = get_object_or_404(
        ClassRoom,
        id=classroom_id
    )

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        section = request.POST.get('section', '').strip()
        academic_year = request.POST.get('academic_year', '').strip()

        if not all([name, academic_year]):
            messages.error(
                request,
                "Please fill all required fields."
            )

        elif ClassRoom.objects.filter(
            name__iexact=name,
            section__iexact=section,
            academic_year__iexact=academic_year
        ).exclude(id=classroom.id).exists():
            messages.error(
                request,
                "This classroom already exists for the selected academic year."
            )

        else:
            try:
                classroom.name = name
                classroom.section = section
                classroom.academic_year = academic_year
                classroom.save()

                messages.success(
                    request,
                    "Classroom updated successfully!"
                )

                return redirect('manage_classrooms')

            except IntegrityError:
                messages.error(
                    request,
                    "Could not update classroom. Please check the details."
                )

    context = {
        'classroom': classroom,
    }

    return render(
        request,
        'admin/edit_classroom.html',
        context
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_classroom(request, classroom_id):

    classroom = get_object_or_404(
        ClassRoom,
        id=classroom_id
    )

    classroom_name = str(classroom)

    try:
        with transaction.atomic():
            classroom.delete()

        messages.success(
            request,
            f"Classroom '{classroom_name}' deleted successfully."
        )

    except ProtectedError:
        messages.error(
            request,
            "Cannot delete this classroom because students or attendance records are linked to it."
        )

    return redirect('manage_classrooms')



# ==============================
# SUBJECT MANAGEMENT
# ==============================

@login_required
@user_passes_test(is_admin)
def manage_subjects(request):
    search = request.GET.get('search', '').strip()

    subjects = Subject.objects.all().order_by('name')

    if search:
        subjects = subjects.filter(
            models.Q(name__icontains=search) |
            models.Q(code__icontains=search) |
            models.Q(description__icontains=search)
        )

    context = {
        'subjects': subjects,
        'search': search,
        'total_subjects': Subject.objects.count(),
        'active_page': 'subjects',
    }

    return render(request, 'admin/manage_subjects.html', context)


@login_required
@user_passes_test(is_admin)
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()

        if not name or not code:
            messages.error(request, 'Subject name and code are required.')

        elif Subject.objects.filter(code__iexact=code).exists():
            messages.error(request, 'This subject code already exists.')

        else:
            try:
                Subject.objects.create(
                    name=name,
                    code=code,
                    description=description
                )

                messages.success(request, 'Subject added successfully!')
                return redirect('manage_subjects')

            except IntegrityError:
                messages.error(request, 'Unable to add subject. Please try again.')

    return render(request, 'admin/add_subject.html')


@login_required
@user_passes_test(is_admin)
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()

        if not name or not code:
            messages.error(request, 'Subject name and code are required.')

        elif Subject.objects.filter(
            code__iexact=code
        ).exclude(id=subject.id).exists():
            messages.error(request, 'This subject code already exists.')

        else:
            subject.name = name
            subject.code = code
            subject.description = description

            try:
                subject.save()
                messages.success(request, 'Subject updated successfully!')
                return redirect('manage_subjects')

            except IntegrityError:
                messages.error(request, 'Unable to update subject.')

    return render(request, 'admin/edit_subject.html', {
        'subject': subject
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    # Prevent deletion if subject is assigned to teachers
    if subject.teacher_assignments.exists():
        messages.error(
            request,
            'This subject is assigned to teachers. Remove its assignments first.'
        )
        return redirect('manage_subjects')

    try:
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')

    except ProtectedError:
        messages.error(
            request,
            'This subject cannot be deleted because attendance records are linked to it.'
        )

    return redirect('manage_subjects')



# ==============================
# TEACHER ASSIGNMENTS MANAGEMENT
# ==============================

@login_required
@user_passes_test(is_admin)
def manage_assignments(request):
    search = request.GET.get('search', '').strip()

    assignments = TeacherAssignment.objects.select_related(
        'teacher__user',
        'classroom',
        'subject'
    ).order_by('classroom__name', 'subject__name')

    if search:
        assignments = assignments.filter(
            models.Q(teacher__user__first_name__icontains=search) |
            models.Q(teacher__user__last_name__icontains=search) |
            models.Q(teacher__user__username__icontains=search) |
            models.Q(classroom__name__icontains=search) |
            models.Q(subject__name__icontains=search) |
            models.Q(subject__code__icontains=search)
        )

    context = {
        'assignments': assignments,
        'search': search,
        'total_assignments': TeacherAssignment.objects.count(),
        'active_page': 'assignments',
    }

    return render(request, 'admin/manage_assignments.html', context)


@login_required
@user_passes_test(is_admin)
def add_assignment(request):
    teachers = TeacherProfile.objects.select_related('user').filter(
        user__is_active=True
    ).order_by('user__first_name')

    classrooms = ClassRoom.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')

        if not all([teacher_id, classroom_id, subject_id]):
            messages.error(request, 'Please select teacher, classroom and subject.')

        else:
            teacher = get_object_or_404(teachers, id=teacher_id)
            classroom = get_object_or_404(classrooms, id=classroom_id)
            subject = get_object_or_404(subjects, id=subject_id)

            if TeacherAssignment.objects.filter(
                teacher=teacher,
                classroom=classroom,
                subject=subject
            ).exists():
                messages.error(request, 'This assignment already exists.')

            else:
                try:
                    TeacherAssignment.objects.create(
                        teacher=teacher,
                        classroom=classroom,
                        subject=subject
                    )

                    messages.success(request, 'Assignment created successfully!')
                    return redirect('manage_assignments')

                except IntegrityError:
                    messages.error(request, 'This assignment already exists.')

    context = {
        'teachers': teachers,
        'classrooms': classrooms,
        'subjects': subjects,
    }

    return render(request, 'admin/add_assignment.html', context)


@login_required
@user_passes_test(is_admin)
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related(
            'teacher__user', 'classroom', 'subject'
        ),
        id=assignment_id
    )

    teachers = TeacherProfile.objects.select_related('user').filter(
        user__is_active=True
    ).order_by('user__first_name')

    classrooms = ClassRoom.objects.all().order_by('name')
    subjects = Subject.objects.all().order_by('name')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')

        if not all([teacher_id, classroom_id, subject_id]):
            messages.error(request, 'Please select all required fields.')

        else:
            teacher = get_object_or_404(teachers, id=teacher_id)
            classroom = get_object_or_404(classrooms, id=classroom_id)
            subject = get_object_or_404(subjects, id=subject_id)

            duplicate = TeacherAssignment.objects.filter(
                teacher=teacher,
                classroom=classroom,
                subject=subject
            ).exclude(id=assignment.id).exists()

            if duplicate:
                messages.error(request, 'This assignment already exists.')

            else:
                assignment.teacher = teacher
                assignment.classroom = classroom
                assignment.subject = subject

                try:
                    assignment.save()
                    messages.success(request, 'Assignment updated successfully!')
                    return redirect('manage_assignments')

                except IntegrityError:
                    messages.error(request, 'Unable to update assignment.')

    context = {
        'assignment': assignment,
        'teachers': teachers,
        'classrooms': classrooms,
        'subjects': subjects,
    }

    return render(request, 'admin/edit_assignment.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(TeacherAssignment, id=assignment_id)

    try:
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')

    except ProtectedError:
        messages.error(
            request,
            'This assignment cannot be deleted because attendance records are linked to it.'
        )

    return redirect('manage_assignments')



# ==============================
# SYSTEM OVERVIEW
# ==============================

@login_required
@user_passes_test(is_admin)
def system_overview(request):

    context = {
        'total_students': StudentProfile.objects.count(),
        'active_students': StudentProfile.objects.filter(
            user__is_active=True
        ).count(),
        'inactive_students': StudentProfile.objects.filter(
            user__is_active=False
        ).count(),

        'total_teachers': TeacherProfile.objects.count(),
        'active_teachers': TeacherProfile.objects.filter(
            user__is_active=True
        ).count(),
        'inactive_teachers': TeacherProfile.objects.filter(
            user__is_active=False
        ).count(),

        'total_classrooms': ClassRoom.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_assignments': TeacherAssignment.objects.count(),

        'recent_students': StudentProfile.objects.select_related(
            'user', 'classroom'
        ).order_by('-id')[:5],

        'recent_assignments': TeacherAssignment.objects.select_related(
            'teacher__user', 'classroom', 'subject'
        ).order_by('-id')[:5],

        'active_page': 'overview',
    }

    return render(request, 'admin/system_overview.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_assignments(request):

    assignments = TeacherAssignment.objects.filter(
        teacher__user=request.user
    ).select_related(
        'classroom',
        'subject'
    ).order_by(
        'classroom__name',
        'subject__name'
    )

    context = {
        'assignments': assignments,
        'total_assignments': assignments.count(),
        'active_page': 'assignments',
    }

    return render(
        request,
        'teacher/my_assignments.html',
        context
    )

@login_required
@user_passes_test(is_student)
def student_profile(request):

    try:
        student = StudentProfile.objects.select_related(
            'user',
            'classroom'
        ).get(user=request.user)

    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('login')

    context = {
        'student': student,
    }

    return render(
        request,
        'student/profile.html',
        context
    )