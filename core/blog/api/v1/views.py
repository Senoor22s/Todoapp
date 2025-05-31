from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from .serializers import TaskSerializer
from ...models import Task
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from .paginations import DefaultPagination
from .filters import TaskFilter

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticatedOrReadOnly,IsAuthorOrReadOnly]
    serializer_class=TaskSerializer
    queryset=Task.objects.all()
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields=['user']
    search_fields=['title','description']
    filterset_class = TaskFilter
    ordering_fields=['created_at']
    pagination_class=DefaultPagination