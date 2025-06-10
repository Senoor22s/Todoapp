from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (TokenRefreshView,TokenVerifyView)

app_name='api-v1'

urlpatterns=[
    path('registration/',RegistrationAPIView.as_view(),name="registration"),
    path('token/login/', CustomObtainAuthToken.as_view(),name='token-login'),
    path('token/logout/',CustomDiscardAuthToken.as_view(),name='token-logout'),
    path('jwt/create/',CustomTokenObtainPairView.as_view(),name='jwt-create'),
    path('jwt/refresh/',TokenRefreshView.as_view(),name='jwt-refresh'),
    path('jwt/verify/',TokenVerifyView.as_view(),name='jwt-verify'),
    path('change-password',ChangePasswordAPIView.as_view(),name='change-password'),
    path('test-email',TestEmailSend.as_view(),name='test-email'),
    path('activation/confirm/<str:token>',ActivationAPIView.as_view(),name='confirm-activation'),
    path('activation/resend',ActivationResendAPIView.as_view(),name='activation'),
    path('profile/',ProfileAPIView.as_view(),name='profile'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('reset-password/confirm/<str:token>/', ConfirmResetPasswordAPIView.as_view(), name='confirm-reset-password'),
]