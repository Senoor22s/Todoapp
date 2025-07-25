"""
URL configuration for core project.

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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import index_view
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view=get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version="v1",
        description="My website API Document",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="legendsdt4@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/',include('blog.urls')),
    path('accounts/',include('accounts.urls')),
    path('api-auth/',include('rest_framework.urls')),
    path('',index_view,name='index'),
    path('api-docs/',include_docs_urls(title='api sample')),
    path('swagger/',schema_view.with_ui('swagger'),name='schema-swagger-ui'),
    path('redoc/',schema_view.with_ui('redoc'),name="schema-redoc"),
    path('swagger/api.json',schema_view.without_ui(),name='schema-json'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)