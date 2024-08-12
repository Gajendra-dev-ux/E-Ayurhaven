from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .validators import validate_username
from .models import Book, Chapter , Heading , Content , Profile 
from .models import Content
# from ckeditor.widgets import CKEditorWidget


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=150, validators=[validate_username])
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'cover']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'email', 'contact_number']

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('name',)

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255)


class HeadingForm(forms.ModelForm):
    class Meta:
        model = Heading
        fields = ('level', 'name', 'parent',)

    def __init__(self, *args, **kwargs):
        chapter = kwargs.pop('chapter', None)
        super().__init__(*args, **kwargs)
        if chapter:
            self.fields['parent'].queryset = Heading.objects.filter(chapter=chapter)
        else:
            self.fields['parent'].queryset = Heading.objects.none()

class ContentForm(forms.ModelForm):
    # text = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Content
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'tinymce'}),
        }
