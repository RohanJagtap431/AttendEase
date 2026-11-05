
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Homepage redirects to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='home'),

    path('', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('attendance/', include('attendance.urls')),
]
