from django.contrib import admin
from .models import Book, Quiz, Question,Answer

# Register your models here.
admin.site.register(Book)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    pass

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
