from django.urls import path,include
from .views import *

app_name='accounts'

urlpatterns=[
    path('',include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
    path("weather/", WeatherAPIView.as_view(),name="weather"),
    path('api/v1/',include('accounts.api.v1.urls')),
]