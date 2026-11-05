from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User
from academics.models import TeacherProfile, ClassRoom
from students.models import StudentProfile


class UserCreateForm(UserCreationForm):

    employee_id = forms.CharField(
        max_length=30,
        required=False
    )

    department = forms.CharField(
        max_length=100,
        required=False
    )

    roll_number = forms.CharField(
        max_length=20,
        required=False
    )

    classroom = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(),
        required=False
    )

    admission_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    parent_name = forms.CharField(
        max_length=100,
        required=False
    )

    parent_phone = forms.CharField(
        max_length=15,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone',
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'teacher':
            if not cleaned_data.get('employee_id'):
                self.add_error('employee_id', 'Employee ID is required.')

        elif role == 'student':
            required_fields = {
                'roll_number': 'Roll Number is required.',
                'classroom': 'Please select a class.',
                'admission_date': 'Admission Date is required.',
            }

            for field, error in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, error)

        return cleaned_data