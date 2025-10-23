"""
URL routing for Reservations app API endpoints.
"""

from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet

router = DefaultRouter()
router.register(r"reservations", ReservationViewSet, basename="reservation")

urlpatterns = router.urls
