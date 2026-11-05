from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    roll_number = models.CharField(max_length=20)

    classroom = models.ForeignKey(
        'academics.ClassRoom',
        on_delete=models.PROTECT,
        related_name='students'
    )

    admission_date = models.DateField()
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['roll_number']
        constraints = [
            models.UniqueConstraint(
                fields=['classroom', 'roll_number'],
                name='unique_student_roll_per_class'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"