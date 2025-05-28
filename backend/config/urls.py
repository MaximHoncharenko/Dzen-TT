from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.utils.html import format_html

def index(request):
    html = format_html("""
        <html>
            <head><title>API коментарів</title></head>
            <body>
                <h1>Ласкаво просимо до API коментарів</h1>
                <p>Цей сервіс дозволяє:</p>
                <ul>
                    <li>Переглядати список головних коментарів (без батьків)</li>
                    <li>Створювати нові коментарі</li>
                    <li>Відповідати на коментарі (рекурсивно)</li>
                    <li>Додавати вкладення (зображення та текстові файли)</li>
                </ul>
                <h2>Основні маршрути API</h2>
                <ul>
                    <li><a href="/api/comments/">Список коментарів (GET, POST)</a></li>
                    <li><a href="/api/comments/&lt;id&gt;/">Перегляд, оновлення, видалення коментаря (GET, PUT, DELETE)</a></li>
                    <li><a href="/api/comments/&lt;id&gt;/reply/">Створення відповіді на коментар (POST)</a></li>
                </ul>
            </body>
        </html>
    """)
    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('comments.urls')),
    path('', index),  # Додаємо головну сторінку
]
