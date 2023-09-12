from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('tasks/<task_id>', views.task_page, name='task_page_by_id'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)