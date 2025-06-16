from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "is_done",
        "created_at",
    )

admin.site.register(Task,TaskAdmin)