from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import Task, TaskType,  TaskFile, TaskSubject
from .forms import TaskForm
from django.http import JsonResponse
from .models import TaskTopic

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
    all_subjects = TaskSubject.objects.all()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['task_subj']
            task_type = form.cleaned_data['task_type']
            topic = form.cleaned_data['topic']
            description = form.cleaned_data['description']
            files = request.FILES.getlist('files')  # Pobierz przesłane pliki jako listę

            # Stwórz zadanie i zapisz je do bazy danych
            task = Task(
                topic=topic,
                description=description,
                author=request.user,
                difficulty=1,
            )
            task.save()

            # Dodaj przesłane pliki do zadania
            for file in files:
                task_file = TaskFile(task=task, file=file)
                task_file.save()

            # Przekieruj użytkownika po dodaniu zadania
            task_id = task.id
            return redirect('task_page_by_id', task_id=task_id)

    else:
        form = TaskForm()
    messages.success(request, "Wystąpił błąd przy dodawaniu zadania!")
    return render(request, 'add_task.html', {'form': form, 'subjects': all_subjects})

@user_passes_test(lambda u: u.is_superuser)
def task_page(request, task_id):
    task = Task.objects.get(pk=task_id)
    return render(request, 'task_page.html', {'task': task})



def load_topics(request):
    type_id = request.GET.get('type_id')
    topics = TaskTopic.objects.filter(type_id=type_id).values_list('id', 'name')
    topic_dict = dict(topics)
    return JsonResponse({'topics': topic_dict})

def load_types(request):
    subject_id = request.GET.get('subject_id')
    types = TaskType.objects.filter(subject_id=subject_id).values_list('id', 'name')
    type_dict = dict(types)
    return JsonResponse({'types': type_dict})