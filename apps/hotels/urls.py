"""
URL routing for Hotels app API endpoints.
"""

from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomTypeViewSet, RoomViewSet

router = DefaultRouter()
router.register(r"hotels", HotelViewSet, basename="hotel")
router.register(r"room-types", RoomTypeViewSet, basename="roomtype")
router.register(r"rooms", RoomViewSet, basename="room")

urlpatterns = router.urls
