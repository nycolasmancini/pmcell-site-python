"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint para Railway"""
    return JsonResponse({
        'status': 'healthy',
        'app': 'PMCELL Catálogo Backend',
        'version': '1.0.0'
    })

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'PMCELL Catálogo API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'health': '/health/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/', api_root, name='api_root'),
    path('', api_root, name='root'),
]

# Servir arquivos estáticos e media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
