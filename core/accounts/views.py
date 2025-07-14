from django.shortcuts import render
from .forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.core.cache import cache
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

OPENWEATHER_API_KEY = "ebcc879477ba4509c9e734ed57869af7"
LOCATION = "Tehran,IR"

class WeatherAPIView(APIView):
    def get(self, request, *args, **kwargs):
        weather = cache.get('weather')
        if weather:
            return Response(weather)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fa"
        res = requests.get(url)
        if res.status_code != 200:
            return Response({'error': 'Service unavailable'}, status=503)
        weather = res.json()
        cache.set('weather', weather, 60*20)
        return Response(weather)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/accounts/login/'
    template_name = 'registration/signup.html'

