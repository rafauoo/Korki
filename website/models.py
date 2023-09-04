from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class TaskType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return (f"{self.name}")

class FileType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return (f"{self.name}")

class Task(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True)
    description = models.TextField()

    def __str__(self) -> str:
        return (f"#{self.id} ({self.type.name})")

def task_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/task_#<id>/<filename>
    return "task_#{0}/{1}".format(instance.task.id, filename)

class TaskFile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.ForeignKey(FileType, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=task_file_path)

    def __str__(self) -> str:
        return (f"#{self.task.id} ({self.task.type.name}): {self.file_type}")

# class AssignmentFiles(models.Model):
#     pass
    
# class TaskAssignment(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE)
#     assigned_user = models.ForeignKey(User, on_delete=models.CASCADE)
#     assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL)
#     due_date = models.DateTimeField()
#     is_sent = models.BooleanField(default=False)
#     is_approved = models.BooleanField(default=False)