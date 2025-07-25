from rest_framework import serializers
from ...models import User,Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(max_length=255,write_only=True)

    class Meta:
        model=User
        fields=['email','password','password1']

    def validate(self, attrs):
        if attrs.get('password')!=attrs.get('password1'):
            raise serializers.ValidationError({'detail':'passwords does not match'})
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop('password1', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    email=serializers.CharField(label=_('Email'),write_only=True)
    password=serializers.CharField(label=_('Password'),style={'input_type':'password'},trim_whitespace=False,write_only=True)
    token=serializers.CharField(label=_('Token'),read_only=True)

    def validate(self,attrs):
        username=attrs.get('email')
        password=attrs.get('password')
        if username and password:
            user=authenticate(request=self.context.get('request'),username=username,password=password)
            if not user:
                msg=_('Unable to login with provided credentials')
                raise serializers.ValidationError(msg,code='authorization')
            if not user.is_verified:
                raise serializers.ValidationError({'detail':'user is not verified'})
        else:
            msg=_('Must include "username" and "password".')
            raise serializers.ValidationError(msg,code='authorization')
        
        attrs['user']=user
        return attrs

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data=super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError({'detail':'user is not verified'})
        validated_data['email']=self.user.email
        validated_data['user_id']=self.user.id 
        return validated_data

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(required=True)
    new_password=serializers.CharField(required=True)
    new_password1=serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs.get('new_password')!=attrs.get('new_password1'):
            raise serializers.ValidationError({'detail':'passwords does not match'})
        try:
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password':list(e.messages)})
        return super().validate(attrs)

class ProfileSerializer(serializers.ModelSerializer):
    email=serializers.CharField(source='user.email',read_only=True)

    class Meta:
        model=Profile
        fields=['id','email','first_name','last_name','image','description']

class ActivationResendSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    def validate(self, attrs):
        email=attrs.get('email')
        try:
            user_obj=User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail':'user does not exist'})
        if user_obj.is_verified:
            raise serializers.ValidationError({'detail':'user already is verified'})
        attrs['user']=user_obj
        return super().validate(attrs)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ConfirmResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    new_password1=serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs.get('new_password')!=attrs.get('new_password1'):
            raise serializers.ValidationError({'detail':'passwords does not match'})
        try:
            validate_password(attrs.get('new_password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password':list(e.messages)})
        return super().validate(attrs)
