from django.urls import path,include
from .views import *

app_name="blog"

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:pk>/done/', TaskDoneToggleView.as_view(), name='task-done-toggle'),
    path('api/v1/',include('blog.api.v1.urls',namespace='api-v1')),
]