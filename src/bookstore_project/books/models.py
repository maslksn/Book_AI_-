from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя автора")
    bio = models.TextField(blank=True, null=True, verbose_name="Биография")
    
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название жанра")
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название книги")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор")
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="Обложка")
    isbn = models.CharField(max_length=17, blank=True, null=True, verbose_name="ISBN")
    published_date = models.DateField(blank=True, null=True, verbose_name="Дата публикации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return f"{self.title} - {self.author.name}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг",
        help_text="Оценка от 1 до 5"
    )
    text = models.TextField(blank=True, null=True, verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('user', 'book')  # Один пользователь — одна оценка на книгу

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.rating}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_completed = models.BooleanField(default=False, verbose_name="Завершен")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"

    @property
    def total_price(self):
        return sum(item.get_total_price() for item in self.orderitem_set.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    quantity = models.IntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def get_total_price(self):
        return self.quantity * self.book.price

    def __str__(self):
        return f"{self.book.title} x{self.quantity}"