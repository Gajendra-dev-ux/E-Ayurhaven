from django.db import models
from django.contrib.auth.models import User
# from ckeditor.fields import RichTextField



class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.ImageField(upload_to='coverimages/', null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.name

class Heading(models.Model):
    LEVEL_CHOICES = (
        (1, 'Heading 1'),
        (2, 'Heading 2'),
        (3, 'Heading 3'),
        (4, 'Heading 4'),
    )

    chapter = models.ForeignKey(Chapter, related_name='headings', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subheadings', on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Content(models.Model):
    heading = models.ForeignKey(Heading, related_name='contents', on_delete=models.CASCADE)
    text = models.TextField()
    def __str__(self):
        return f"Content for {self.heading.name}"

# Create your models here.
class LoginRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'