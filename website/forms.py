from django import forms
from .models import TaskType, TaskTopic, TaskSubject, TaskLevel
from django.contrib.auth.models import User

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class TaskForm(forms.Form):
    task_subj = forms.ModelChoiceField(queryset=TaskSubject.objects.all(), empty_label=None)
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.all(), empty_label=None)
    topic = forms.ModelChoiceField(queryset=TaskTopic.objects.all(), empty_label=None)
    description = forms.CharField(max_length=2048, widget=forms.Textarea)
    files = MultipleFileField(required=False)  # Użyj naszej nowej MultipleFileField
    level = forms.ModelChoiceField(queryset=TaskLevel.objects.all(), empty_label=None)
    diff = forms.IntegerField(max_value=100, min_value=0, step_size=1)

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)


class AdminFilterTaskForm(forms.Form):
    task_subj = forms.ModelChoiceField(queryset=TaskSubject.objects.all(), empty_label=None, required=False)
    level = forms.ModelChoiceField(queryset=TaskLevel.objects.all(), empty_label=None, required=False)
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.all(), empty_label=None, required=False)
    topic = forms.ModelChoiceField(queryset=TaskTopic.objects.all(), empty_label=None, required=False)
    min_diff = forms.IntegerField(max_value=100, min_value=0, step_size=1, required=False)
    max_diff = forms.IntegerField(max_value=100, min_value=0, step_size=1, required=False)

class AssignTask(forms.Form):
    user = forms.CharField(required=True)
    deadline = forms.DateTimeField(required=True)

class AddResponse(forms.Form):
    description=forms.CharField(max_length=2048, widget=forms.Textarea, required=False)
    files=MultipleFileField(required=False)