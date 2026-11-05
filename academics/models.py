from django.conf import settings
from django.db import models


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True)
    academic_year = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'section']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'section', 'academic_year'],
                name='unique_classroom'
            )
        ]

    def __str__(self):
        return f"{self.name} {self.section} ({self.academic_year})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'classroom', 'subject'],
                name='unique_teacher_assignment'
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.classroom}"