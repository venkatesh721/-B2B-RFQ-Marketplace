from django.utils import timezone
from rest_framework import serializers

from .models import Quotation, RFQ


class RFQSerializer(serializers.ModelSerializer):
    buyer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RFQ
        fields = (
            "id",
            "buyer",
            "product_or_service_name",
            "requirement_description",
            "quantity",
            "delivery_location",
            "deadline",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "buyer", "status", "created_at", "updated_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value

    def create(self, validated_data):
        return RFQ.objects.create(buyer=self.context["request"].user, **validated_data)


class SupplierRFQSerializer(RFQSerializer):
    """RFQ representation for suppliers; buyer identity is deliberately hidden."""

    class Meta(RFQSerializer.Meta):
        fields = (
            "id",
            "product_or_service_name",
            "requirement_description",
            "quantity",
            "delivery_location",
            "deadline",
            "status",
            "created_at",
            "updated_at",
        )


class QuotationSerializer(serializers.ModelSerializer):
    """Validates a supplier's quotation and exposes server-controlled ownership."""

    supplier = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Quotation
        fields = (
            "id", "rfq", "supplier", "quoted_price", "estimated_delivery_time",
            "message", "created_at", "updated_at",
        )
        read_only_fields = ("id", "supplier", "created_at", "updated_at")

    def validate_quoted_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quoted price must be greater than 0.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        rfq = attrs["rfq"]

        if rfq.status != RFQ.Status.OPEN:
            raise serializers.ValidationError({"rfq": "Quotations can only be submitted to open RFQs."})
        if rfq.deadline <= timezone.now():
            raise serializers.ValidationError({"rfq": "Quotations cannot be submitted after the RFQ deadline."})
        if rfq.buyer_id == request.user.id:
            raise serializers.ValidationError({"rfq": "You cannot quote on your own RFQ."})
        if Quotation.objects.filter(rfq=rfq, supplier=request.user).exists():
            raise serializers.ValidationError({"rfq": "You have already submitted a quotation for this RFQ."})
        return attrs

    def create(self, validated_data):
        return Quotation.objects.create(supplier=self.context["request"].user, **validated_data)
