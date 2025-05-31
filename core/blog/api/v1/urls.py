from rest_framework.routers import DefaultRouter
from .views import *

app_name="api-v1"

router=DefaultRouter()
router.register('tasks',TaskViewSet,basename='tasks')
urlpatterns=router.urls