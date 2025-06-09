from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView
from .serializers import (RegistrationSerializer,CustomAuthTokenSerializer,CustomTokenObtainPairSerializer,ChangePasswordSerializer,
                          ProfileSerializer,ActivationResendSerializer,ResetPasswordSerializer,ConfirmResetPasswordSerializer)
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ...models import Profile
from mail_templated import send_mail,EmailMessage
from ..utils import EmailThread
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from jwt.exceptions import InvalidSignatureError,ExpiredSignatureError
from django.conf import settings

User=get_user_model()

class RegistrationAPIView(GenericAPIView):
    serializer_class=RegistrationSerializer

    def post(self,requset,*args,**kwargs):
        serializer=RegistrationSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email=serializer.validated_data['email']
        data={'email':email}
        user_obj=get_object_or_404(User,email=email)
        token=self.get_tokens_for_user(user_obj)
        email_obj=EmailMessage('email/activation.tpl',{'token':token},'test@test.com',[email])
        EmailThread(email_obj).start()
        return Response(data,status=status.HTTP_201_CREATED)
    def get_tokens_for_user(self,user):
        refresh=RefreshToken.for_user(user)
        return str(refresh.access_token)

class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class=CustomAuthTokenSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]

    def post(self,request,*args,**kwargs):
        serializer=CustomAuthTokenSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        token,created=Token.objects.get_or_create(user=user)
        return Response({'token':token.key,'user_id':user.pk,'email':user.email})

class CustomDiscardAuthToken(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        if not self.request.user.is_verified:
            return Response({'detail':'user is not verified'})
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class=CustomTokenObtainPairSerializer

class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    model = User

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get("old_password")
            new_password = serializer.validated_data.get("new_password")
            if not self.object.check_password(old_password):
                return Response({'old_password': ["wrong password"]}, status=status.HTTP_400_BAD_REQUEST)
            if old_password == new_password:
                return Response({'new_password': ["New password cannot be the same as the old password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(new_password)
            self.object.save()
            return Response({'detail': 'Password successfully changed'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]

    def get_object(self):
        queryset=self.get_queryset()
        obj=get_object_or_404(queryset,user=self.request.user)
        return obj

class TestEmailSend(GenericAPIView):
    def get(self,request,*args,**kwargs):
        self.email='legendsdt2@gmail.com'
        user_obj=get_object_or_404(User,email=self.email)
        token=self.get_tokens_for_user(user_obj)
        email_obj=EmailMessage('email/activation.tpl',{'token':token},'test@test.com',[self.email])
        EmailThread(email_obj).start()
        return Response({'email sent'})
    def get_tokens_for_user(self,user):
        refresh=RefreshToken.for_user(user)
        return str(refresh.access_token)

class ActivationAPIView(APIView):
    def get(self,request,token,*args,**kwargs):
        try:
            token=jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
            user_id=token.get('user_id')
        except ExpiredSignatureError:
            return Response({'detail':'token has been expired'},status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'detail':'token is not valid'},status=status.HTTP_400_BAD_REQUEST)
        user_obj=User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response({'detail':'your account already has been verified'})
        user_obj.is_verified=True
        user_obj.save()
        return Response({'detail':'your account has been verified successfully'})

class ActivationResendAPIView(GenericAPIView):
    serializer_class=ActivationResendSerializer
    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj=serializer.validated_data['user']
        token=self.get_tokens_for_user(user_obj)
        email_obj=EmailMessage('email/activation.tpl',{'token':token},'test@test.com',[user_obj.email])
        EmailThread(email_obj).start()
        return Response({'detail':'user activation resend successfully'},status=status.HTTP_200_OK)
    
    def get_tokens_for_user(self,user):
        refresh=RefreshToken.for_user(user)
        return str(refresh.access_token)


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        token = self.get_tokens_for_user(user)
        reset_link = f"http://127.0.0.1:8000/accounts/api/v1/reset-password/confirm/{token}"

        
        email_obj = EmailMessage(
            'email/reset.tpl',
            {'token': token, 'reset_link': reset_link},
            'no-reply@example.com',
            [email]
        )
        EmailThread(email_obj).start()

        return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class ConfirmResetPasswordAPIView(GenericAPIView):
    serializer_class = ConfirmResetPasswordSerializer
    permission_classes = [AllowAny]

    def put(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('user_id')
        except ExpiredSignatureError:
            return Response({'detail': 'Token has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data['new_password']

        if user.check_password(new_password):
            return Response({'new_password': ['New password cannot be the same as the old password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
