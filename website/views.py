from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import Task

# Create your views here.
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['passwd']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Zalogowano pomyślnie!")
            return redirect(request.GET.get("next", "home"))
        else:
            messages.success(request, "Nie udało się zalogować!")
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def home(request):
    return render(request, 'home.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "Wylogowano pomyślnie")
    return redirect('home')

@login_required
def tasks(request):
    all_tasks = Task.objects.all()
    return render(request, 'tasks.html', {'all_tasks': all_tasks})

@user_passes_test(lambda u: u.is_superuser)
def add_task(request):
    return render(request, 'add_task.html', {})

@user_passes_test(lambda u: u.is_superuser)
def task_page(request, task_id):
    task = Task.objects.get(pk=task_id)
    return render(request, 'task_page.html', {'task': task})

