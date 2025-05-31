from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_snippet(self):
        if len(self.description) > 6:
            return self.description[:6] + '...'
        else:
            return self.description[:6]
        
    def get_absolute_api_url(self):
        return reverse('blog:api-v1:tasks-detail', kwargs={'pk':self.id})
