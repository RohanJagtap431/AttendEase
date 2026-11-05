from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .forms import UserCreateForm
from academics.models import TeacherProfile
from students.models import StudentProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    add_form = UserCreateForm

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'phone'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'email',
                'first_name',
                'last_name',
                'role',
                'phone',
                'employee_id',
                'department',
                'roll_number',
                'classroom',
                'admission_date',
                'parent_name',
                'parent_phone',
            ),
        }),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'phone',
        'is_staff',
        'is_active',
    )

    list_filter = ('role', 'is_staff', 'is_active')

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            if obj.role == 'teacher':
                TeacherProfile.objects.create(
                    user=obj,
                    employee_id=form.cleaned_data['employee_id'],
                    department=form.cleaned_data.get('department', '')
                )

            elif obj.role == 'student':
                StudentProfile.objects.create(
                    user=obj,
                    roll_number=form.cleaned_data['roll_number'],
                    classroom=form.cleaned_data['classroom'],
                    admission_date=form.cleaned_data['admission_date'],
                    parent_name=form.cleaned_data.get('parent_name', ''),
                    parent_phone=form.cleaned_data.get('parent_phone', '')
                )