from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.utils.html import format_html
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from comments import views  # Import the views module from the comments app

def index(request):
    html = format_html("""
        <html>
            <head>
                <title>API коментарів</title>
                <style>
                    .btn {{
                        display: inline-block;
                        padding: 10px 20px;
                        margin: 5px;
                        font-size: 16px;
                        color: white;
                        background-color: #007bff;
                        border: none;
                        border-radius: 4px;
                        text-decoration: none;
                        cursor: pointer;
                    }}
                    .btn:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <h1>Ласкаво просимо до API коментарів</h1>
                <p>Цей сервіс дозволяє:</p>
                <ul>
                    <li>Переглядати список головних коментарів (без батьків)</li>
                    <li>Створювати нові коментарі</li>
                    <li>Відповідати на коментарі (рекурсивно)</li>
                    <li>Додавати вкладення (зображення та текстові файли)</li>
                </ul>

                <h2>Документація API</h2>
                <a href="/swagger/" class="btn">Swagger UI</a>
                <a href="/redoc/" class="btn">Redoc</a>
                <a href="/api/docs/" class="btn">Swagger UI (Alt)</a>

                <h2>Сторінка з коментарями</h2>
                <a href="/api/comments/page/" class="btn">Сторінка коментарів</a>
            </body>
        </html>
    """)
    return HttpResponse(html)




    

# 🔻 Swagger schema setup
schema_view = get_schema_view(
   openapi.Info(
      title="Comments API",
      default_version='v1',
      description="API для коментарів із вкладеними відповідями, сортуванням, пагінацією тощо.",
      contact=openapi.Contact(email="max@example.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('comments.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-alt'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', index),  # головна сторінка
    path('comments/', include('comments.urls')),  # URL для коментарів
    path('page/', views.comments_page, name='comments-page'),

]