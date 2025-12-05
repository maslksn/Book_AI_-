from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Book, Author, Genre, Review
from .recommendations import BookRecommender

def home(request):
    """Главная страница с рекомендациями"""
    latest_books = Book.objects.all().order_by('-created_at')[:6] 
    # AI рекомендации популярных книг
    recommender = BookRecommender()
    popular_books = recommender.get_popular_books(n_recommendations=6)
    
    context = {
        'latest_books': latest_books,
        'popular_books': popular_books,
        'page_title': 'Главная - Книжный магазин'
    }
    return render(request, 'books/home.html', context)

def book_list(request):
    """Страница со всем каталогом книг"""
    books = Book.objects.all().order_by('title')
    
    # Фильтрация по жанру
    genre_id = request.GET.get('genre')
    if genre_id:
        books = books.filter(genres__id=genre_id)
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        books = books.filter(title__icontains=search_query)
    
    # Пагинация - 12 книг на страницу
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    genres = Genre.objects.all()
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'page_title': 'Каталог книг'
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, book_id):
    """Детальная страница книги с AI-рекомендациями"""
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book).order_by('-created_at')
    
    similar_books = []
    
    # Пробуем использовать AI для рекомендаций
    try:
        recommender = BookRecommender()
        similar_book_ids = recommender.get_similar_books(book_id, n_recommendations=4)
        
        if similar_book_ids:
            similar_books = Book.objects.filter(id__in=similar_book_ids)
    except Exception as e:
        # Если AI сломался, используем fallback
        print(f"AI recommendation error: {e}")
    
    # Если AI не сработал или вернул мало книг, используем жанры
    if not similar_books:
        similar_books = Book.objects.filter(
            genres__in=book.genres.all()
        ).exclude(id=book.id).distinct()[:4]
    
    context = {
        'book': book,
        'reviews': reviews,
        'similar_books': similar_books,
        'page_title': book.title
    }
    return render(request, 'books/book_detail.html', context)

def author_list(request):
    """Список авторов"""
    authors = Author.objects.all().order_by('name')
    context = {
        'authors': authors,
        'page_title': 'Авторы'
    }
    return render(request, 'books/author_list.html', context)

def author_detail(request, author_id):
    """Детальная страница автора"""
    author = get_object_or_404(Author, id=author_id)
    books = Book.objects.filter(author=author)
    
    context = {
        'author': author,
        'books': books,
        'page_title': f'Книги автора {author.name}'
    }
    return render(request, 'books/author_detail.html', context)