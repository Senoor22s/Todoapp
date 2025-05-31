# filters.py
from django_filters import ModelMultipleChoiceFilter,FilterSet
from accounts.models import User
from blog.models import Task

# select multiple user with click+ctrl
class TaskFilter(FilterSet):
    user = ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='user',
        to_field_name='id'
    )
    class Meta:
        model = Task
        fields = ['user']