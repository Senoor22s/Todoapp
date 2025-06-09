from django.shortcuts import render
from .forms import CustomUserCreationForm
from django.views.generic import CreateView

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = '/accounts/login/'
    template_name = 'registration/signup.html'

