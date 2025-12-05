import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Book
import json

# Русские стоп-слова
RUSSIAN_STOP_WORDS = [
    'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его',
    'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от',
    'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже',
    'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом',
    'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их',
    'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда',
    'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти',
    'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при',
    'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про',
    'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой',
    'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю',
    'между'
]

class BookRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=RUSSIAN_STOP_WORDS,  # Используем наш список русских стоп-слов
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.book_ids = []
        self.is_fitted = False
    
    def prepare_data(self):
        """Подготавливает данные о книгах для обучения"""
        books = Book.objects.all()
        
        if len(books) < 2:
            return False
            
        book_data = []
        for book in books:
            # Создаем текстовое представление книги
            text = f"{book.title} {book.author.name} "
            if book.description:
                text += book.description
            # Добавляем жанры
            genres = " ".join([genre.name for genre in book.genres.all()])
            text += f" {genres}"
            
            book_data.append({
                'id': book.id,
                'text': text
            })
            self.book_ids.append(book.id)
        
        # Создаем TF-IDF матрицу
        texts = [item['text'] for item in book_data]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.is_fitted = True
        
        return True
    
    def get_similar_books(self, book_id, n_recommendations=5):
        """Возвращает похожие книги для заданной книги"""
        if not self.is_fitted:
            if not self.prepare_data():
                return []
        
        try:
            # Находим индекс книги в нашем списке
            book_index = self.book_ids.index(book_id)
            
            # Вычисляем косинусное сходство
            cosine_similarities = cosine_similarity(
                self.tfidf_matrix[book_index], 
                self.tfidf_matrix
            ).flatten()
            
            # Получаем индексы самых похожих книг (исключая саму книгу)
            similar_indices = cosine_similarities.argsort()[-n_recommendations-1:-1][::-1]
            
            # Возвращаем ID похожих книг
            similar_book_ids = [self.book_ids[i] for i in similar_indices]
            
            return similar_book_ids
            
        except (ValueError, IndexError):
            return []
    
    def get_popular_books(self, n_recommendations=5):
        """Возвращает популярные книги (заглушка - можно улучшить)"""
        return Book.objects.all().order_by('-id')[:n_recommendations]