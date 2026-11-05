from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive.")
                return redirect('login')

            login(request, user)
            return redirect('dashboard_redirect')

        messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


@login_required
def dashboard_redirect(request):

    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('admin_dashboard')

    elif request.user.role == 'teacher':
        return redirect('teacher_dashboard')

    elif request.user.role == 'student':
        return redirect('student_dashboard')

    logout(request)
    messages.error(request, "Your account has an invalid role.")
    return redirect('login')


@login_required
def logout_view(request):

    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')

    return redirect('dashboard_redirect')