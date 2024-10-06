from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import BookForm,NoteForm
from .models import Book,Note
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import Profile
from django.contrib.auth import authenticate
from .forms import EditProfileForm
from django.contrib.auth import logout
from django.core.files.base import ContentFile
import base64
from .models import Book, Chapter, Heading, Content, Bookmark
from .forms import  ChapterForm, HeadingForm, ContentForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Heading
import re
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import json
from django.db.models import Q
from bs4 import BeautifulSoup


def home(request):
    content_query = request.GET.get('content_q')
    title_query = request.GET.get('title_q')
    books = Book.objects.all()

    content_results = []
    heading_results = []
    chapter_results = []
    book_results = []
    results = []

    if title_query:
        books = Book.objects.filter(title__icontains=title_query)
    else:
        books = Book.objects.all()

    if content_query:
        # Fetch all matching results with annotations
        content_results = Content.objects.filter(
            Q(text__icontains=content_query)
        )

        heading_results = Heading.objects.filter(
            Q(name__icontains=content_query)
        )

        chapter_results = Chapter.objects.filter(
            Q(name__icontains=content_query)
        )

        book_results = Book.objects.filter(
            Q(title__icontains=content_query)
        )

        if content_results:
            results.append(content_results)
        
        if heading_results:
            results.append(heading_results)
        
        if chapter_results:
            results.append(chapter_results)
        
        if book_results:
            results.append(book_results)

    # Check for each book if the user has it bookmarked
    for book in books:
        if request.user.is_authenticated:
            book.is_bookmarked = Bookmark.objects.filter(user=request.user, book=book).exists()
        else:
            book.is_bookmarked = False


    context = {
        'books': books,
        'content_results': content_results,
        'heading_results': heading_results,
        'chapter_results': chapter_results,
        'book_results': book_results,
        'results': results,
        'content_query': content_query,
        'title_query': title_query,
    }

    return render(request, 'ocr_app/home.html', context)




def view_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    books = Book.objects.all()  # Retrieve all books to populate the dropdown
    chapters = book.chapters.all()[:1]
    query = request.GET.get('q', '')

    occurrences = 0

    if query:
        query_lower = query.lower()
        regex = re.compile(re.escape(query), re.IGNORECASE)

        for chapter in chapters:
            chapter.highlighted_name = regex.sub(lambda match: f'<span class="highlight">{match.group(0)}</span>', chapter.name)
            if query_lower in chapter.name.lower():
                occurrences += len(regex.findall(chapter.name))

            for heading in chapter.headings.all():
                heading.highlighted_name = regex.sub(lambda match: f'<span class="highlight">{match.group(0)}</span>', heading.name)
                if query_lower in heading.name.lower():
                    occurrences += len(regex.findall(heading.name))

                for content in heading.contents.all():
                    content.highlighted_text = regex.sub(lambda match: f'<span class="highlight">{match.group(0)}</span>', content.text)
                    if query_lower in content.text.lower():
                        occurrences += len(regex.findall(content.text))
    else:
        for chapter in chapters:
            chapter.highlighted_name = chapter.name
            for heading in chapter.headings.all():
                heading.highlighted_name = heading.name
                for content in heading.contents.all():
                    content.highlighted_text = content.text

    # Filter headings by level and organize them by chapter
    chapters_with_headings = []
    for chapter in chapters:
        chapter_headings = {
            'chapter': chapter,
            'heading1': chapter.headings.filter(level=1),
            'heading2': chapter.headings.filter(level=2),
            'heading3': chapter.headings.filter(level=3),
            'heading4': chapter.headings.filter(level=4),
        }
        chapters_with_headings.append(chapter_headings)

    return render(request, 'ocr_app/view_book.html', {
        'book': book,
        'books': books,  # Include the books in the context
        'chapters_with_headings': chapters_with_headings,
        'query': query,
        'occurrences': occurrences,
    })

@login_required
def write_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    chapters = Chapter.objects.filter(book=book)
    headings = Heading.objects.filter(chapter__book=book)

    # Filter headings by level and organize them by chapter
    chapters_with_headings = []
    for chapter in chapters:
        chapter_headings = {
            'chapter': chapter,
            'heading1': chapter.headings.filter(level=1),
            'heading2': chapter.headings.filter(level=2),
            'heading3': chapter.headings.filter(level=3),
            'heading4': chapter.headings.filter(level=4),
        }
        chapters_with_headings.append(chapter_headings)

    return render(request, 'ocr_app/write_book.html',  {
        'book': book,
        'chapters': chapters,
        'headings': headings,
        'chapters_with_headings': chapters_with_headings,
    })
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'ocr_app/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check and create profile if it doesn't exist
                if not hasattr(user, 'profile'):
                    Profile.objects.create(user=user)
                auth_login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'ocr_app/login.html', {'form': form})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            return redirect('profile')
    else:
        form = BookForm()
    return render(request, 'ocr_app/add_book.html', {'form': form})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('profile')
    return render(request, 'ocr_app/confirm_delete.html', {'book': book})

@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        next_url = request.POST.get('next', reverse('home'))
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_url)
    else:
        next_url = request.GET.get('next', reverse('home'))
        form = BookForm(instance=book)
    return render(request, 'ocr_app/edit_book.html', {'form': form, 'book': book, 'next': next_url})




@login_required
def add_chapter(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.book = book
            chapter.save()
            return redirect('write_book',book_id)
    else:
        form = ChapterForm()
    return render(request, 'ocr_app/add_chapter.html', {'form': form, 'book': book})

def edit_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            return redirect('write_book', chapter.book.id)
    else:
        form = ChapterForm(instance=chapter)
    return render(request, 'ocr_app/edit_chapter.html', {'form': form, 'chapter': chapter})


@login_required
def add_heading(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    book = chapter.book
    book_id = book.id

    if request.method == 'POST':
        form = HeadingForm(request.POST, chapter=chapter)
        if form.is_valid():
            heading = form.save(commit=False)
            heading.chapter = chapter
            heading.save()
            return redirect('write_book', book_id=book_id)
    else:
        form = HeadingForm(chapter=chapter)

    return render(request, 'ocr_app/add_heading.html', {'form': form, 'chapter': chapter, 'book': book})

def edit_heading(request, heading_id):
    heading = get_object_or_404(Heading, id=heading_id)
    chapter = heading.chapter
    book = chapter.book
    book_id = book.id

    if request.method == 'POST':
        form = HeadingForm(request.POST, chapter=chapter, instance=heading)
        if form.is_valid():
            form.save()
            return redirect('write_book', book_id=book_id)
    else:
        form = HeadingForm(chapter=chapter, instance=heading)

    return render(request, 'ocr_app/edit_heading.html', {'form': form, 'heading': heading, 'chapter':chapter, 'book':book})

@login_required
def add_content(request, heading_id):
    heading = get_object_or_404(Heading, id=heading_id)
    Chapter = heading.chapter
    book = Chapter.book
    book_id = book.id
    
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = request.POST.get('content', '').strip()  # Trim whitespace
            content = form.save(commit=False)
            content.heading = heading
            content.save()
            return redirect('write_book',book_id)
    else:
        form = ContentForm()

    return render(request, 'ocr_app/add_content.html', {'form': form, 'heading': heading, 'chapter': Chapter, 'book':book})


def edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect('write_book', book_id=content.heading.chapter.book.id)
    else:
        form = ContentForm(instance=content)
    return render(request, 'ocr_app/edit_content.html', {'form': form, 'content': content})



def get_headings(request):
    parent_id = request.GET.get('parent_id')
    level = request.GET.get('level')

    if parent_id:
        if 'chapter-' in parent_id:
            parent_id = parent_id.replace('chapter-', '')
        if level == '1':
            headings = Heading.objects.filter(chapter_id=parent_id, level=1)
        else:
            headings = Heading.objects.filter(parent_id=parent_id, level=level)
    else:
        headings = []

    data = [{'id': heading.id, 'name': heading.name} for heading in headings]
    return JsonResponse(data, safe=False)

@login_required
def profile(request):
    books = Book.objects.all()

    # query = request.GET.get('q')
    # if query:
    #     books = Book.objects.filter(title__icontains=query)
    # else:
    #     books = Book.objects.all()
    bookmarks = Bookmark.objects.filter(user=request.user)
    
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('complete_profile')  # Redirect to a view where they can complete their profile

    # Clear the logged_out flag
    request.session['logged_out'] = False

    return render(request, 'ocr_app/profile.html', {'profile': profile , 'bookmarks': bookmarks,'books':books})

def logout_view(request):
    logout(request)
    # Set a session flag to indicate the user has logged out
    request.session['logged_out'] = True
    return redirect('home')


@login_required
@login_required
def edit_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Redirect to a view where they can complete their profile
        return redirect('edit_profile')

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            cropped_image_data = request.POST.get('cropped_image_data')
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,')
                ext = format.split('/')[-1]
                profile_image = ContentFile(base64.b64decode(imgstr), name=f'{request.user.username}_profile.{ext}')
                profile.profile_image = profile_image
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'ocr_app/edit_profile.html', {'form': form})



@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    next_url = request.GET.get('next', reverse('home'))  # Default to 'home' if 'next' is not provided

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_url)
    else:
        form = BookForm(instance=book)
    return render(request, 'ocr_app/edit_book.html', {'form': form, 'book': book, 'next': next_url})

def delete_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if request.method == 'POST':
        chapter.delete()
        return redirect('write_book', book_id=chapter.book.id)
    return render(request, 'ocr_app/delete_chapter.html', {'chapter': chapter})

def delete_heading(request, heading_id):
    heading = get_object_or_404(Heading, id=heading_id)
    if request.method == 'POST':
        heading.delete()
        return redirect('write_book', book_id=heading.chapter.book.id)
    return render(request, 'ocr_app/delete_heading.html', {'heading': heading})

def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        content.delete()
        return redirect('write_book', book_id=content.heading.chapter.book.id)
    return render(request, 'ocr_app/delete_content.html', {'content': content})
def clean_paragraph_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove span tags but keep their content
    for span in soup.find_all('span'):
        span.unwrap()

    # Remove br tags but keep their content
    for br in soup.find_all('br'):
        br.unwrap()

    # Convert the cleaned soup back to a string
    cleaned_text = str(soup)
    return cleaned_text

def update_or_add_style(styles, name, **kwargs):
    if name in styles:
        style = styles[name]
        for key, value in kwargs.items():
            setattr(style, key, value)
    else:
        styles.add(ParagraphStyle(name=name, **kwargs))

def download_book_pdf(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Create a HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    Story = []

    # Get default styles and define custom styles
    styles = getSampleStyleSheet()

    # Custom styles for indentation
    update_or_add_style(styles, 'Heading1', parent=styles['Heading1'], leftIndent=15)
    update_or_add_style(styles, 'Heading2', parent=styles['Heading2'], leftIndent=25)
    update_or_add_style(styles, 'Heading3', parent=styles['Heading3'], leftIndent=35)
    update_or_add_style(styles, 'Heading4', parent=styles['Heading4'], leftIndent=45)
    update_or_add_style(styles, 'BodyTextIndented', parent=styles['BodyText'], leftIndent=15)

    # Add the title and author
    title = Paragraph(book.title, styles['Title'])
    author = Paragraph(f"Author: {book.author}", styles['Normal'])
    Story.append(title)
    Story.append(author)
    Story.append(Spacer(1, 1))

    # Add chapters, headings, and content
    for chapter in book.chapters.all():
        chapter_title = Paragraph(chapter.name, styles['Heading1'])
        Story.append(chapter_title)
        Story.append(Spacer(1, 2))  # Space between chapter title and content

        for heading1 in chapter.headings.filter(level=1):
            heading1_title = Paragraph(heading1.name, styles['Heading2'])
            Story.append(heading1_title)
            Story.append(Spacer(1, 2))  # Space between heading1 and its content

            for content in heading1.contents.all():
                cleaned_text = clean_paragraph_text(content.text.replace('\n', '<br />'))
                content_paragraph = Paragraph(cleaned_text, styles['BodyTextIndented'])
                Story.append(content_paragraph)

            for heading2 in chapter.headings.filter(level=2, parent_id=heading1.id):
                heading2_title = Paragraph(heading2.name, styles['Heading3'])
                Story.append(heading2_title)
                Story.append(Spacer(1, 2))  # Space between heading2 and its content

                for content in heading2.contents.all():
                    cleaned_text = clean_paragraph_text(content.text.replace('\n', '<br />'))
                    content_paragraph = Paragraph(cleaned_text, styles['BodyTextIndented'])
                    Story.append(content_paragraph)

                for heading3 in chapter.headings.filter(level=3, parent_id=heading2.id):
                    heading3_title = Paragraph(heading3.name, styles['Heading4'])
                    Story.append(heading3_title)
                    Story.append(Spacer(1, 2))  # Space between heading3 and its content

                    for content in heading3.contents.all():
                        cleaned_text = clean_paragraph_text(content.text.replace('\n', '<br />'))
                        content_paragraph = Paragraph(cleaned_text, styles['BodyTextIndented'])
                        Story.append(content_paragraph)

                    for heading4 in chapter.headings.filter(level=4, parent_id=heading3.id):
                        heading4_title = Paragraph(heading4.name, styles['BodyTextIndented'])
                        Story.append(heading4_title)
                        Story.append(Spacer(1, 2))  # Space between heading4 and its content

                        for content in heading4.contents.all():
                            cleaned_text = clean_paragraph_text(content.text.replace('\n', '<br />'))
                            content_paragraph = Paragraph(cleaned_text, styles['BodyTextIndented'])
                            Story.append(content_paragraph)

    # Build the PDF
    doc.build(Story)

    return response

def edit_chapter_view(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_name = data.get('name')

            # Update chapter name
            chapter.name = new_name
            chapter.save()

            return JsonResponse({'message': 'Chapter updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import json
from .models import Chapter, Heading

@csrf_protect
def update_chapter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            chapter = Chapter.objects.get(id=data['id'])
            chapter.name = data['value']
            chapter.save()
            return JsonResponse({'success': True})
        except Chapter.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chapter not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
def update_heading(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            heading = Heading.objects.get(id=data['id'])
            heading.name = data['value']
            heading.save()
            return JsonResponse({'success': True})
        except Heading.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Heading not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
def bookmark_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, book=book)
    if created:
        # The bookmark was added
        message = "Bookmarked successfully!"
    else:
        # If the bookmark already exists, remove it
        bookmark.delete()
        message = "Bookmark removed!"
    
    return redirect('home')  # Redirect to book detail page or any other page

@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'my_bookmarks.html', {'bookmarks': bookmarks})


@login_required
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('list_notes')
    else:
        form = NoteForm()
    return render(request, 'ocr_app/add_note.html', {'form': form})

@login_required
def list_notes(request):
    notes = Note.objects.filter(user=request.user)
    return render(request, 'ocr_app/list_notes.html', {'notes': notes})

@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('list_notes')
    else:
        form = NoteForm(instance=note)
    return render(request, 'ocr_app/edit_note.html', {'form': form})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('list_notes')
    return render(request, 'ocr_app/delete_note.html', {'note': note})


from django.shortcuts import render, redirect
from .models import Quiz, Question, Answer, UserScore
from .forms import QuizForm, QuestionForm, AnswerForm

def list_quizzes(request):
    quizzes = Quiz.objects.all()
    return render(request, 'ocr_app/list_quizzes.html', {'quizzes': quizzes})

def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer:
                answer = Answer.objects.get(id=selected_answer)
                if answer.is_correct:
                    score += 1
        UserScore.objects.create(user=request.user, quiz=quiz, score=score)
        return redirect('quiz_results', quiz_id=quiz.id)
    return render(request, 'ocr_app/take_quiz.html', {'quiz': quiz, 'questions': questions})

def quiz_results(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    user_score = UserScore.objects.filter(user=request.user, quiz=quiz).first()
    return render(request, 'ocr_app/quiz_results.html', {'quiz': quiz, 'user_score': user_score})

def view_plant_3d(request):
    return render(request,'ocr_app/view_plant_3d.html')



import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

# Function to call the ChatGPT API
def call_chatgpt_api(prompt):
    api_key = settings.OPENAI_API_KEY
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',  # Or another GPT model
        'messages': [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        'temperature': 0.7,
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
    print(response.json())  # Print the entire response for debugging
    return response.json()


# A Django view to send input to ChatGPT
def chatgpt_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        try:
            response_data = call_chatgpt_api(user_input)
            print("Processed Response Data:", response_data)  # Debugging output
            if response_data.get('choices'):
                choices = response_data['choices']
                if choices:
                    gpt_reply = choices[0].get('message', {}).get('content', 'No content found')
                else:
                    gpt_reply = 'No choices found in response'
            else:
                gpt_reply = 'API response does not contain choices'
        except requests.exceptions.RequestException as e:
            gpt_reply = "Request failed: " + str(e)
        except Exception as e:
            gpt_reply = "Error occurred: " + str(e)
        return JsonResponse({'response': gpt_reply})
    return render(request, 'ocr_app/chat.html')
