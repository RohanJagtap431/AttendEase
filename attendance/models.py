from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.PROTECT,
        related_name='attendance_records'
    )

    assignment = models.ForeignKey(
        'academics.TeacherAssignment',
        on_delete=models.PROTECT,
        related_name='attendance_records'
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='present'
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='marked_attendance'
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__roll_number']

        constraints = [
            models.UniqueConstraint(
                fields=['student', 'assignment', 'date'],
                name='unique_student_attendance_per_subject_date'
            )
        ]

        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['student', 'date']),
        ]

    def clean(self):
        if self.student_id and self.assignment_id:
            if self.student.classroom_id != self.assignment.classroom_id:
                raise ValidationError(
                    "Student does not belong to the assigned classroom."
                )

        if self.marked_by_id and self.marked_by.role != 'teacher':
            if not self.marked_by.is_superuser:
                raise ValidationError(
                    "Only teachers or superusers can mark attendance."
                )

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.assignment.subject} - "
            f"{self.date} - {self.status}"
        )