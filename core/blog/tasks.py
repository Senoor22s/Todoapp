from celery import shared_task
from .models import Task

@shared_task
def delete_done_tasks():
    Task.objects.filter(is_done=True).delete()
