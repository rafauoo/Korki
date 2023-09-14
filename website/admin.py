from django.contrib import admin
from .models import Task, TaskType, TaskFile, FileType
from .models import Assignment, AssignmentStatus, Response, ResponseFile, TaskTopic, TaskSubject, TaskLevel, TaskAssignment
# Register your models here.
admin.site.register(Task)
admin.site.register(TaskFile)
admin.site.register(FileType)
admin.site.register(TaskType)
admin.site.register(Assignment)
admin.site.register(AssignmentStatus)
admin.site.register(Response)
admin.site.register(ResponseFile)
admin.site.register(TaskTopic)
admin.site.register(TaskSubject)
admin.site.register(TaskLevel)
admin.site.register(TaskAssignment)