from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MyQuotationListView, QuotationCreateView, RFQViewSet


router = DefaultRouter()
router.register("rfqs", RFQViewSet, basename="rfq")

urlpatterns = [
    path("quotations/", QuotationCreateView.as_view(), name="quotation-list"),
    path("quotations/my/", MyQuotationListView.as_view(), name="quotation-my"),
] + router.urls
