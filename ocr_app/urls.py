from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView 
from django.conf import settings
from django.conf.urls.static import static
from .views import get_headings, edit_chapter as edit_chapter_view, edit_heading, edit_content

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('add/', views.add_book, name='add_book'),
    path('write_book/<int:book_id>/', views.write_book, name='write_book'),
    path('add_chapter/<int:book_id>/', views.add_chapter, name='add_chapter'),
    path('add_heading/<int:chapter_id>/', views.add_heading, name='add_heading'),
    path('add_content/<int:heading_id>/', views.add_content, name='add_content'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('view/<int:book_id>/', views.view_book, name='view_book'),
    path('logout/', CustomLogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('api/headings/', get_headings, name='get_headings'),
    path('edit_heading/<int:heading_id>/', edit_heading, name='edit_heading'),
    path('edit_content/<int:content_id>/', edit_content, name='edit_content'),
    path('edit_chapter/<int:chapter_id>/', views.edit_chapter, name='edit_chapter'),
    path('delete_chapter/<int:chapter_id>/', views.delete_chapter, name='delete_chapter'),
    path('delete_heading/<int:heading_id>/', views.delete_heading, name='delete_heading'),
    path('delete_content/<int:content_id>/', views.delete_content, name='delete_content'),
    path('download_book_pdf/<int:book_id>/', views.download_book_pdf, name='download_book_pdf'),
    path('api/chapters/<int:chapter_id>/edit/', edit_chapter_view, name='edit_chapter_api'),
    path('api/update_chapter/', views.update_chapter, name='update_chapter'),
    path('api/update_heading/', views.update_heading, name='update_heading'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
