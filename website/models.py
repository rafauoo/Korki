from django.db import models
from django.contrib.auth.models import User
# Create your models here.
def response_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/assignments/#<assignment_id>/responses/<response_id>/<filename>
    return "assignments/#{0}/responses/#{1}/{2}".format(instance.response.assignment.id, instance.response.id, filename)

def task_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/assignments/#<assignment_id>/responses/<response_id>/<filename>
    return "tasks/{0}/{1}/{2}/#{3}/{4}".format(instance.task.topic.type.subject.name, instance.task.topic.type.name, instance.task.topic.name, instance.task.id, filename)

class TaskLevel(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return (f"{self.name}")


class TaskSubject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return (f"{self.name}")

class TaskType(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(TaskSubject, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        subj = "Brak"
        if self.subject is not None:
            subj = self.subject.name
        return (f"[{subj}] {self.name}")

class TaskTopic(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        typ = "Brak"
        subj = "Brak"
        if self.type is not None:
            typ = self.type.name
            if self.type.subject is not None:
                subj = self.type.subject.name
        return (f"[{subj}] ({typ}) {self.name}")

class Task(models.Model):
    topic = models.ForeignKey(TaskTopic, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=2048)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    difficulty = models.IntegerField(null=True)
    level = models.ForeignKey(TaskLevel, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        typ = "Brak"
        temat = "Brak"
        subj = "Brak"
        if self.topic is not None:
            temat = self.topic.name
            if self.topic.type:
                typ = self.topic.type.name
                if self.topic.type.subject:
                    subj = self.topic.type.subject.name
        return (f"#{self.id} [{subj}] ({typ}, {temat})")

class FileType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return (f"{self.name}")

class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.ForeignKey(FileType, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=task_file_path)

    def __str__(self) -> str:
        typ = "Brak"
        if self.type is not None:
            typ = self.type.name
        return (f"#{self.task.id}, {typ}")

class AssignmentStatus(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return (f"{self.name}")

class Assignment(models.Model):
    due_date = models.DateTimeField()
    assigned_user = models.ForeignKey(User, related_name='assignments', on_delete=models.CASCADE)
    created_date = models.DateTimeField()
    assigned_by = models.ForeignKey(User, related_name='assigned_assignments', on_delete=models.CASCADE)
    status = models.ForeignKey(AssignmentStatus, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return (f"#{self.id}: for {self.assigned_user.username} due {self.due_date}")

class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return (f"Assigment #{self.assignment.id} (for {self.assignment.assigned_user.username} due {self.assignment.due_date}), Task #{self.task.id}")

class Response(models.Model):
    date_created = models.DateTimeField()
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self) -> str:
        return (f"#{self.id} [{self.date_created}]: Assigment #{self.assignment.id} (for {self.assignment.assigned_user.username} due {self.assignment.due_date})")


class ResponseFile(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    type = models.ForeignKey(FileType, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=response_file_path)

    def __str__(self) -> str:
        typ = "Brak"
        if self.type is not None:
            typ = self.type.name
        return (f"#{self.response.id}, {typ}")


