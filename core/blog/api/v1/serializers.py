from rest_framework import serializers
from ...models import Task
from accounts.models import Profile
from django.urls import reverse

class TaskSerializer(serializers.ModelSerializer):
    snippet=serializers.ReadOnlyField(source='get_snippet')
    relative_url=serializers.URLField(source='get_absolute_api_url',read_only=True)
    absolute_url=serializers.SerializerMethodField()

    class Meta:
        model=Task
        fields= ['id','user','title','description','snippet','relative_url','absolute_url','is_done','is_done','created_at']
        read_only_fields=['user']

    def get_absolute_url(self,obj):
        request=self.context.get('request')
        relative_url = reverse('blog:api-v1:tasks-detail',kwargs={'pk':obj.id})
        return request.build_absolute_uri(relative_url)
    
    def get_fields(self):
        fields = super().get_fields()
        view = self.context.get('view')
        if view and view.action in ['retrieve','create','update', 'partial_update']:
            fields.pop('snippet', None)
            fields.pop('relative_url', None)
            fields.pop('absolute_url', None)
        else:
            fields.pop('description', None)
        return fields
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
