from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('add_task/', views.add_task, name='add_task'),
    path('load_topics/', views.load_topics, name='load_topics'),
    path('load_types/', views.load_types, name='load_types'),
    path('tasks/<task_id>', views.task_page, name='task_page_by_id'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<assignment_id>', views.assignment_page, name='assignment_page_by_id'),
    path('add_task_to_cart/', views.add_task_to_cart, name='add_task_to_cart'),
    path('remove_task_from_cart/', views.remove_task_from_cart, name='remove_task_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('search_user/', views.search_user, name='search_user'),
    path('upload_response/<assignment_id>', views.upload_response, name='upload_response'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)