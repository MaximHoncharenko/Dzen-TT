from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from comments.views import index
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from users.views import MyTokenObtainPairView


schema_view = get_schema_view(
    openapi.Info(
        title="Comments API",
        default_version='v1',
        description="API для коментарів із вкладеними відповідями, сортуванням, пагінацією тощо.",
        contact=openapi.Contact(email="max@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # <-- скобки, не список!
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('comments.urls')),

    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('', index),  # головна сторінка з HTML+JS
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
