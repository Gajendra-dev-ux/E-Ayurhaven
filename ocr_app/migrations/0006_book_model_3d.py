# Generated by Django 5.1.1 on 2024-09-12 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_app', '0005_question_quiz_answer_question_quiz_userscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='model_3d',
            field=models.FileField(blank=True, null=True, upload_to='models3d/'),
        ),
    ]
