import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import User, Profile
from blog.models import Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def common_user(db):
    user = User.objects.create_user(email="user1@test.com", password="testpass123")
    Profile.objects.create(user=user)
    return user

@pytest.fixture
def another_user(db):
    user = User.objects.create_user(email="user2@test.com", password="testpass123")
    Profile.objects.create(user=user)
    return user

@pytest.fixture
def user_task(common_user):
    return Task.objects.create(
        user=common_user,
        title="User Task",
        description="User's task description",
        is_done=False,
    )

@pytest.mark.django_db
class TestTaskAPI:

    def test_authenticated_user_can_create_task(self, api_client, common_user):
        api_client.force_authenticate(user=common_user)
        url = reverse("blog:api-v1:tasks-list")
        data = {
            "title": "New Task",
            "description": "Some description",
            "is_done": False
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert response.data["title"] == "New Task"

    def test_unauthenticated_user_cannot_create_task(self, api_client):
        url = reverse("blog:api-v1:tasks-list")
        data = {
            "title": "Blocked Task",
            "description": "Should fail",
            "is_done": False
        }
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_list_tasks(self, api_client, user_task):
        url = reverse("blog:api-v1:tasks-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_retrieve_single_task(self, api_client, user_task):
        url = reverse("blog:api-v1:tasks-detail", kwargs={"pk": user_task.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["id"] == user_task.id

    def test_user_can_update_own_task(self, api_client, common_user, user_task):
        api_client.force_authenticate(user=common_user)
        url = reverse("blog:api-v1:tasks-detail", kwargs={"pk": user_task.id})
        data = {
            "title": "Updated Task",
            "description": "Updated desc",
            "is_done": True,
        }
        response = api_client.put(url, data)
        assert response.status_code == 200
        assert response.data["title"] == "Updated Task"

    def test_other_user_cannot_update_task(self, api_client, another_user, user_task):
        api_client.force_authenticate(user=another_user)
        url = reverse("blog:api-v1:tasks-detail", kwargs={"pk": user_task.id})
        data = {
            "title": "Hack Update",
            "description": "Hacked!",
            "is_done": True,
        }
        response = api_client.put(url, data)
        assert response.status_code == 403

    def test_user_can_delete_own_task(self, api_client, common_user, user_task):
        api_client.force_authenticate(user=common_user)
        url = reverse("blog:api-v1:tasks-detail", kwargs={"pk": user_task.id})
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_other_user_cannot_delete_task(self, api_client, another_user, user_task):
        api_client.force_authenticate(user=another_user)
        url = reverse("blog:api-v1:tasks-detail", kwargs={"pk": user_task.id})
        response = api_client.delete(url)
        assert response.status_code == 403

    def test_search_tasks(self, api_client, user_task):
        url = reverse("blog:api-v1:tasks-list")
        response = api_client.get(url, {"search": "User"})
        assert response.status_code == 200
        assert any("User" in t["title"] for t in response.data["results"])

    def test_filter_tasks_by_user(self, api_client, common_user, user_task):
        url = reverse("blog:api-v1:tasks-list")
        response = api_client.get(url, {"user": common_user.id})
        assert response.status_code == 200
        assert all(task["user"] == common_user.id for task in response.data["results"])

    def test_ordering_tasks(self, api_client, user_task):
        url = reverse("blog:api-v1:tasks-list")
        response = api_client.get(url, {"ordering": "created_at"})
        assert response.status_code == 200
