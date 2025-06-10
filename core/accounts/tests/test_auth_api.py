import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, Profile
from rest_framework import status

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def new_user(db):
    user = User.objects.create_user(email="user@example.com", password="StrongPass123!", is_verified=True)
    Profile.objects.filter(user=user).delete()
    Profile.objects.create(user=user)
    return user

@pytest.fixture
def unverified_user(db):
    user = User.objects.create_user(email="noverify@example.com", password="StrongPass123!", is_verified=False)
    Profile.objects.filter(user=user).delete()
    Profile.objects.create(user=user)
    return user

@pytest.fixture
def access_token_for_user(new_user):
    refresh = RefreshToken.for_user(new_user)
    return str(refresh.access_token)

@pytest.fixture
def access_token_for_unverified(unverified_user):
    refresh = RefreshToken.for_user(unverified_user)
    return str(refresh.access_token)

@pytest.mark.django_db
class TestAuthAPI:

    def test_registration_success(self, api_client):
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password1": "StrongPass123!"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_token_login_success(self, api_client, new_user):
        url = reverse("accounts:api-v1:token-login")
        response = api_client.post(url, {"email": new_user.email, "password": "StrongPass123!"})
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_token_login_unverified(self, api_client, unverified_user):
        url = reverse("accounts:api-v1:token-login")
        response = api_client.post(url, {"email": unverified_user.email, "password": "StrongPass123!"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"][0]== "user is not verified"

    def test_jwt_login_success(self, api_client, new_user):
        url = reverse("accounts:api-v1:jwt-create")
        response = api_client.post(url, {"email": new_user.email, "password": "StrongPass123!"})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_change_password_success(self, api_client, new_user, access_token_for_user):
        url = reverse("accounts:api-v1:change-password")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token_for_user}")
        data = {
            "old_password": "StrongPass123!",
            "new_password": "NewPass456!",
            "new_password1": "NewPass456!"
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_profile_retrieve(self, api_client, new_user, access_token_for_user):
        url = reverse("accounts:api-v1:profile")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token_for_user}")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == new_user.email

    def test_profile_update(self, api_client, new_user, access_token_for_user):
        url = reverse("accounts:api-v1:profile")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token_for_user}")
        data = {"first_name": "John", "last_name": "Doe",'description':'...'}
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "John"

    def test_activation_resend_success(self, api_client, unverified_user):
        url = reverse("accounts:api-v1:activation")
        data = {"email": unverified_user.email}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_activation_confirm_success(self, api_client, unverified_user, access_token_for_unverified):
        url = reverse("accounts:api-v1:confirm-activation", kwargs={"token": access_token_for_unverified})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "your account has been verified successfully"

    def test_reset_password_request_success(self, api_client, new_user):
        url = reverse("accounts:api-v1:reset-password")
        response = api_client.post(url, {"email": new_user.email})
        assert response.status_code == status.HTTP_200_OK

    def test_confirm_reset_password_success(self, api_client, new_user, access_token_for_user):
        url = reverse("accounts:api-v1:confirm-reset-password", kwargs={"token": access_token_for_user})
        data = {
            "new_password": "NewResetPass123!",
            "new_password1": "NewResetPass123!"
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Password has been reset successfully."
