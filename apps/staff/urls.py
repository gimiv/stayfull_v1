"""
URL routing for Staff app API endpoints.
"""

from rest_framework.routers import DefaultRouter
from .views import StaffViewSet

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')

urlpatterns = router.urls
