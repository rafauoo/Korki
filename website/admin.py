from django.contrib import admin
from .models import Task, TaskFile, FileType, TaskType
# Register your models here.
admin.site.register(Task)
admin.site.register(TaskFile)
admin.site.register(FileType)
admin.site.register(TaskType)