# Generated by Django 4.2 on 2023-10-09 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_lesson_lessonrole_teacherstudents_lessonusers'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='html',
            field=models.TextField(default='None'),
            preserve_default=False,
        ),
    ]