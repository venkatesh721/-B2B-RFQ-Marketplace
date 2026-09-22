from django.db import IntegrityError, transaction
from rest_framework import filters, generics, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import User
from users.permissions import CanViewRFQ, IsBuyer, IsBuyerOrSupplier, IsRFQBuyer, IsSupplier, visible_rfqs_for

from .models import Quotation, RFQ
from .serializers import QuotationSerializer, RFQSerializer, SupplierRFQSerializer


class RFQPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class RFQViewSet(viewsets.ModelViewSet):
    """Buyer-only CRUD endpoints for RFQs."""

    serializer_class = RFQSerializer
    pagination_class = RFQPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["product_or_service_name", "delivery_location"]

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            if user.role == User.Role.BUYER:
                return RFQ.objects.filter(buyer=user)
            queryset = visible_rfqs_for(user)
            return self._apply_supplier_filters(queryset)
        if self.action == "retrieve" and user.role == User.Role.SUPPLIER:
            return visible_rfqs_for(user)
        return RFQ.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsBuyer()]
        if self.action == "list":
            return [IsBuyerOrSupplier()]
        if self.action == "retrieve":
            return [CanViewRFQ()]
        return [IsRFQBuyer()]

    def get_serializer_class(self):
        if self.request.user.role == User.Role.SUPPLIER:
            return SupplierRFQSerializer
        return RFQSerializer

    def _apply_supplier_filters(self, queryset):
        product_name = self.request.query_params.get("product_or_service_name")
        delivery_location = self.request.query_params.get("delivery_location")

        if product_name:
            queryset = queryset.filter(product_or_service_name__icontains=product_name)
        if delivery_location:
            queryset = queryset.filter(delivery_location__icontains=delivery_location)
        return queryset

    @action(detail=True, methods=["get"], url_path="quotations")
    def quotations(self, request, pk=None):
        """Return quotations only to the buyer who owns the RFQ."""
        rfq = self.get_object()
        return Response(QuotationSerializer(rfq.quotations.all(), many=True).data)


class QuotationCreateView(generics.CreateAPIView):
    serializer_class = QuotationSerializer
    permission_classes = [IsSupplier]

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError as error:
            # The serializer handles normal duplicates; this covers concurrent requests.
            raise serializers.ValidationError(
                {"rfq": "You have already submitted a quotation for this RFQ."}
            ) from error


class MyQuotationListView(generics.ListAPIView):
    serializer_class = QuotationSerializer
    permission_classes = [IsSupplier]

    def get_queryset(self):
        return Quotation.objects.filter(supplier=self.request.user).select_related("rfq")
