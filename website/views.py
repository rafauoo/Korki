from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import Task, TaskType,  TaskFile, TaskSubject, TaskLevel, Assignment, AssignmentStatus, TaskAssignment, Response, ResponseFile
from django.contrib.auth.models import User
from .forms import TaskForm, AdminFilterTaskForm, AssignTask, AddResponse
from django.http import JsonResponse, HttpResponse
from .models import TaskTopic
import os
import re
from .models import task_file_path
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import datetime

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
    choice = {}
    cart = request.session.get('cart', [])
    poss_types = TaskType.objects.all()
    poss_topics = TaskTopic.objects.all()
    filtered_tasks = Task.objects.all()
    all_subjects = TaskSubject.objects.all()
    all_levels = TaskLevel.objects.all()
    if request.method == 'POST':
        form = AdminFilterTaskForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['task_subj']:
                filtered_tasks = filtered_tasks.filter(
                    topic__type__subject__name=form.cleaned_data['task_subj']
                )
                poss_types = poss_types.filter(
                    subject__name = form.cleaned_data['task_subj']
                )
            if form.cleaned_data['task_type']:
                filtered_tasks = filtered_tasks.filter(
                    topic__type__name=form.cleaned_data['task_type']
                )
                poss_topics = poss_topics.filter(
                    type__name = form.cleaned_data['task_type']
                )
            if form.cleaned_data['topic']:
                filtered_tasks = filtered_tasks.filter(
                    topic__name=form.cleaned_data['topic']
                )
            if form.cleaned_data['level']:
                filtered_tasks = filtered_tasks.filter(
                    level__name=form.cleaned_data['level']
                )
            if form.cleaned_data['min_diff']:
                filtered_tasks = filtered_tasks.filter(
                    difficulty__gte=form.cleaned_data['min_diff']
                )
            if form.cleaned_data['max_diff']:
                filtered_tasks = filtered_tasks.filter(
                    difficulty__lte=form.cleaned_data['max_diff']
                )
            choice['task_subj'] = form.cleaned_data.get('task_subj')
            choice['task_type'] = form.cleaned_data.get('task_type')
            choice['topic'] = form.cleaned_data.get('topic')
            choice['level'] = form.cleaned_data.get('level')
            choice['min_diff'] = form.cleaned_data.get('min_diff')
            choice['max_diff'] = form.cleaned_data.get('max_diff')
            return render(request, 'tasks.html', {'form': form, 'all_tasks': filtered_tasks, 'subjects': all_subjects, 
                                                  'levels': all_levels, 'choice': choice, 'types': poss_types, 'topics': poss_topics, 'cart': cart})
    else:
        print(cart)
        form = AdminFilterTaskForm()
        
    return render(request, 'tasks.html', {'form': form, 'all_tasks': filtered_tasks, 'subjects': all_subjects, 'levels': all_levels, 'cart': cart})

@user_passes_test(lambda u: u.is_superuser)
def add_task(request):
    all_subjects = TaskSubject.objects.all()
    all_levels = TaskLevel.objects.all()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['task_subj']
            task_type = form.cleaned_data['task_type']
            topic = form.cleaned_data['topic']
            view_content = form.cleaned_data['view_content']
            html = form.cleaned_data['html']
            level = form.cleaned_data['level']
            diff = form.cleaned_data['diff']

            # img
            img_tags = re.findall(r'<img.*?src=["\'](.*?)["\']', view_content)
            img_ids = re.findall(r'<img.*?id=["\'](.*?)["\']', view_content)
            img_ids = [img_id[7:] + os.path.splitext(img_tags[i])[1] for i, img_id in enumerate(img_ids)]
            img_data = zip(img_ids, img_tags)

            task = Task(
                difficulty=diff,
                level=level,
                topic=topic,
                html=html,
                description=view_content,
                author=request.user,
            )
            task.save()
            # Dodaj przesłane pliki do zadania
            for img_id, img_src in img_data:
                task_file = TaskFile(task=task, file=img_src)
                task_file.save()
                dest_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, task_file_path(task_file, img_id)))
                src_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, img_src.replace('/media/', '')))
                print(f"DEST PATH: {dest_path}")
                print(f"SRC PATH: {src_path}")
                dest_dir = os.path.dirname(dest_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                os.rename(src_path, dest_path)
                view_content = view_content.replace(img_src, '/media/' + task_file_path(task_file, img_id))
                html = html.replace(img_src, '/media/' + task_file_path(task_file, img_id))
                task_file.file = task_file_path(task_file, img_id)
                task_file.save()
            
            task.description = view_content
            task.save()
            task.html = html
            task.save()
            # Przekieruj użytkownika po dodaniu zadania
            task_id = task.id
            return redirect('task_page_by_id', task_id=task_id)
        else:
            messages.success(request, "Wystąpił błąd przy dodawaniu zadania!")
    else:
        form = TaskForm()

    return render(request, 'add_task.html', {'form': form, 'subjects': all_subjects, 'levels': all_levels})

@user_passes_test(lambda u: u.is_superuser)
def task_page(request, task_id):
    task = Task.objects.get(pk=task_id)
    files = TaskFile.objects.filter(task=task_id)
    cart = request.session.get('cart', [])
    return render(request, 'task_page.html', {'task': task, 'files': files, 'cart': cart})


@user_passes_test(lambda u: u.is_superuser)
def load_topics(request):
    type_id = request.GET.get('type_id')
    topics = TaskTopic.objects.filter(type_id=type_id).values_list('id', 'name')
    topic_dict = dict(topics)
    return JsonResponse({'topics': topic_dict})

@user_passes_test(lambda u: u.is_superuser)
def load_types(request):
    subject_id = request.GET.get('subject_id')
    types = TaskType.objects.filter(subject_id=subject_id).values_list('id', 'name')
    type_dict = dict(types)
    return JsonResponse({'types': type_dict})

@login_required
def assignments(request):
    my_assignments = Assignment.objects.filter(assigned_user=request.user)
    my_assignments_accepted = my_assignments.filter(status=AssignmentStatus.objects.get(name="Zaakceptowany"))
    my_assignments_active = my_assignments.filter(Q(status=AssignmentStatus.objects.get(name="Wysłany")) | Q(status=AssignmentStatus.objects.get(name="Odesłany")))
    return render(request, 'assignments.html', {'my_assignments_accepted': my_assignments_accepted, 'my_assignments_active': my_assignments_active})

@login_required
def add_task_to_cart(request):
    # Pobierz identyfikator zadania z argumentów URL
    task_id = request.POST.get('task_id')

    # Pobierz zadanie o danym identyfikatorze lub zwróć błąd 404, jeśli nie istnieje
    task = get_object_or_404(Task, id=task_id)

    # Pobierz lub utwórz koszyk w sesji
    cart = request.session.get('cart', [])
    if task_id in cart:
        print(cart)
        response_data = {'message': f'Zadanie #{task_id} już jest w koszyku.', 'success': False}
        return JsonResponse(response_data)
    # Dodaj identyfikator zadania do koszyka
    cart.append(task_id)
    
    print(cart)
    # Zapisz koszyk z powrotem do sesji
    request.session['cart'] = cart

    # Zwróć odpowiedź JSON, która może zawierać informacje zwrotne o sukcesie lub błędzie
    response_data = {'message': f'Zadanie #{task_id} zostało dodane do koszyka.', 'success': True}
    return JsonResponse(response_data)

@login_required
def remove_task_from_cart(request):
    # Pobierz identyfikator zadania z argumentów URL
    task_id = request.POST.get('task_id')
    # Pobierz zadanie o danym identyfikatorze lub zwróć błąd 404, jeśli nie istnieje
    task = get_object_or_404(Task, id=task_id)

    # Pobierz lub utwórz koszyk w sesji
    cart = request.session.get('cart', [])
    print(cart)
    if task_id in cart:
        cart.remove(task_id)
        print(cart)
        request.session['cart'] = cart
        response_data = {'message': f'Zadanie #{task_id} zostało usunięte z koszyka', 'success': True}
        return JsonResponse(response_data)
    # Zwróć odpowiedź JSON, która może zawierać informacje zwrotne o sukcesie lub błędzie
    response_data = {'message': f'Zadanie #{task_id} nie zostało usunięte z koszyka.', 'success': False}
    return JsonResponse(response_data)

@login_required
def cart(request):
    cart = request.session.get('cart', [])
    tasks = Task.objects.filter(id__in=cart)
    if request.method == 'POST':
        form = AssignTask(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            deadline = form.cleaned_data['deadline']
            user = User.objects.get(username=username)
            if not user:
                messages.success(request, "Nie znaleziono takiego użytkownika!")
                return render(request, 'cart.html', {'tasks': tasks, 'form': form})
            
            assignment = Assignment(
                due_date=deadline,
                assigned_user=user,
                created_date=datetime.datetime.now(),
                assigned_by=request.user,
                status=AssignmentStatus.objects.get(name="Wysłany")
            )
            assignment.save()
            for task_id in cart:
                task_ass = TaskAssignment(task=Task.objects.get(pk=task_id), assignment=Assignment.objects.get(pk=assignment.id))
                task_ass.save()
            cart = []
            request.session['cart'] = cart
            messages.success(request, f"Udało się przypisać zadanie dla {user}!")
            return redirect('home')
        else:
            messages.success(request, "Wystąpił błąd przy przypisywaniu zadania!")
    else:
        form = AssignTask()
    return render(request, 'cart.html', {'tasks': tasks, 'form': form})

@login_required
def search_user(request):
    username = request.POST.get('text')
    users = User.objects.filter(username__icontains=username)
    user_list = [{'id': user.id, 'username': user.username} for user in users]
    print(user_list)
    return JsonResponse(user_list, safe=False)

@login_required
def assignment_page(request, assignment_id):
    assignment = Assignment.objects.get(pk=assignment_id)
    ass_tasks = TaskAssignment.objects.filter(assignment=assignment)
    responses = Response.objects.filter(assignment=assignment)
    responses_with_files = []
    now = datetime.datetime.now()
    for response in responses:
        response_files = ResponseFile.objects.filter(response=response)
        responses_with_files.append((response, response_files))
    task_list = []
    for task in ass_tasks:
        task_list.append(task.task)
    return render(request, 'assignment_page.html', {'assignment': assignment, 'tasks': task_list, 'responses': responses_with_files, 'now': now})

@login_required
def upload_response(request, assignment_id):
    if request.method == 'POST':
        form = AddResponse(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['description']
            files = request.FILES.getlist('files')
            acceptTask = form.cleaned_data['acceptTask']
            if not description and not files:
                messages.success(request, f"Nie można wysłać pustej odpowiedzi!")
                return redirect('assignment_page_by_id', assignment_id)
            response = Response(
                date_created=datetime.datetime.now(),
                assignment=Assignment.objects.get(pk=assignment_id),
                description=description,
                author=request.user
            )
            response.save()

            for file in files:
                print(file)
                resp_file = ResponseFile(response=response, file=file, name=file)
                resp_file.save()
            assignment = Assignment.objects.get(pk=assignment_id)
            assignmentu = Assignment.objects.filter(pk=assignment_id)
            if request.user == assignment.assigned_by:
                if acceptTask:
                    assignmentu.update(status=AssignmentStatus.objects.get(name="Zaakceptowany"))
                elif assignment.status.name == "Odesłany":
                    assignmentu.update(status=AssignmentStatus.objects.get(name="Wysłany"))
            if request.user == assignment.assigned_user and assignment.status.name == "Wysłany":

                assignmentu.update(status=AssignmentStatus.objects.get(name="Odesłany"))
    return redirect('assignment_page_by_id', assignment_id)

@login_required
def assigned_by_me(request):
    assignments = Assignment.objects.filter(assigned_by=request.user)
    assignments_sent = assignments.filter(status=AssignmentStatus.objects.get(name="Wysłany"))
    assignments_sent_back = assignments.filter(status=AssignmentStatus.objects.get(name="Odesłany"))
    assignments_accepted = assignments.filter(status=AssignmentStatus.objects.get(name="Zaakceptowany"))
    return render(request, 'assigned_by_me.html', {'ass_sent': assignments_sent, 'ass_back': assignments_sent_back, 'ass_acc': assignments_accepted })

@login_required
def lessons(request):
    return render(request, 'lessons.html', {})

@user_passes_test(lambda u: u.is_superuser)
def add_lesson(request):
    subjects = TaskSubject.objects.all()
    return render(request, 'add_lesson.html', {'subjects': subjects})


@csrf_exempt
def upload_temp_file(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']

        # Ustal folder docelowy dla obrazków tymczasowych
        temp_image_folder = os.path.join(settings.MEDIA_ROOT, 'temp_images')
        
        # Upewnij się, że folder istnieje (jeśli nie, utwórz go)
        os.makedirs(temp_image_folder, exist_ok=True)

        # Wygeneruj unikalną nazwę dla obrazka
        image_name = uploaded_image.name
        image_path = os.path.join(temp_image_folder, image_name)

        # Zapisz przesłany obrazek do folderu tymczasowego
        with open(image_path, 'wb') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        # Zwróć URL obrazka
        image_url = os.path.join(settings.MEDIA_URL, 'temp_images', image_name)
        return JsonResponse({'image_url': image_url})
    else:
        return JsonResponse({'error': 'Brak obrazka lub metoda nieprawidłowa'}, status=400)

def generate_pdf_from_tasks(request):
    import pdfkit

    #Define path to wkhtmltopdf.exe
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    tasks = request.session.get('cart', [])
    #Define path to HTML file
    tasks = sorted(tasks)
    #Point pdfkit configuration to wkhtmltopdf.exe
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    import bs4

    # load the file
    with open("./website/assets/PDF_sample.html") as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, 'html.parser')
    print(soup)
    # create new link
    for id, task in enumerate(tasks):
        new_tag = soup.new_tag("h3")
        new_tag.string = f"Zadanie {id+1}."
        new_tag['style'] = "font-size: 20px; font-family: Arial, Helvetica, sans-serif;"
        # insert it into the document
        soup.body.append(new_tag)
        taskk = Task.objects.get(id=task)
        new_tag = soup.new_tag("p")
        new_tag.string = taskk.description.replace("src=\"/media/", "src=\"http:/127.0.0.1:8000/media/")
        soup.body.append(new_tag)
        new_tag = soup.new_tag("div")
        new_tag['style'] = "font-size: 8px; color: grey; float: right;"
        new_tag.string = f"#{task}"
        soup.body.append(new_tag)
        new_tag = soup.new_tag("br")
        soup.body.append(new_tag)

    with open("temp_file2.html", "w") as outf:
         outf.write(str(soup).replace("&lt;img", "<img").replace("%\"gt;", "%\">"))
    options = {
        'quiet': '',
        'javascript-delay' : '500',
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'disable-smart-shrinking': '',
        'dpi': '400',
    }
    file_path = f"{str(datetime.datetime.now())}{request.user}".replace(" ", "").replace(":", "o").replace(".","a").replace("-", "o")
    print(file_path)
    pdfkit.from_string(str(soup).replace("&lt;img", "<img").replace("%\"gt;", "%\">"), output_path=f'./media/temp_files/{file_path}.pdf', configuration=config, options=options)
    return JsonResponse({'file_path': file_path})

def download_pdf(request):
    file_path = f"{request.GET['file_name']}.pdf"
    with open(f"./media/temp_files/{file_path}", "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="zadania.pdf"'
        return response

def clear_cart(request):
    request.session['cart'] = []
    return JsonResponse({'message': "Wyczyszczono koszyk!"})