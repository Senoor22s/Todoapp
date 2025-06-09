from django.urls import path,include
from accounts.views import SignUpView

app_name='accounts'

urlpatterns=[
    path('',include('django.contrib.auth.urls')),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('api/v1/',include('accounts.api.v1.urls')),
]