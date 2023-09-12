from django import forms
from .models import TaskType, TaskTopic, TaskSubject

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
    description = forms.CharField(max_length=255, widget=forms.Textarea)
    files = MultipleFileField(required=False)  # Użyj naszej nowej MultipleFileField

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)