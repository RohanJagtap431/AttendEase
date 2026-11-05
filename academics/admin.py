from django.contrib import admin
from .models import (
    ClassRoom,
    Subject,
    TeacherProfile,
    TeacherAssignment
)

admin.site.register(ClassRoom)
admin.site.register(Subject)
admin.site.register(TeacherProfile)
admin.site.register(TeacherAssignment)