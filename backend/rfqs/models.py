from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class RFQ(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfqs",
    )
    product_or_service_name = models.CharField(max_length=255)
    requirement_description = models.TextField()
    quantity = models.PositiveIntegerField()
    delivery_location = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline"]
        indexes = [
            models.Index(fields=["status", "deadline"], name="rfq_status_deadline_idx"),
            models.Index(fields=["buyer", "created_at"], name="rfq_buyer_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="rfq_quantity_positive",
            ),
        ]

    def clean(self):
        errors = {}
        if self.buyer_id and self.buyer.role != self.buyer.Role.BUYER:
            errors["buyer"] = "Only users with the BUYER role can create RFQs."
        if self._state.adding and self.deadline and self.deadline <= timezone.now():
            errors["deadline"] = "Deadline must be in the future."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.product_or_service_name


class Quotation(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="quotations")
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quotations",
    )
    quoted_price = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_delivery_time = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["supplier", "created_at"], name="quote_supplier_created_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["rfq", "supplier"],
                name="unique_supplier_quote_per_rfq",
            ),
            models.CheckConstraint(
                condition=Q(quoted_price__gt=0),
                name="quotation_price_positive",
            ),
        ]

    def clean(self):
        errors = {}
        if self.supplier_id and self.supplier.role != self.supplier.Role.SUPPLIER:
            errors["supplier"] = "Only users with the SUPPLIER role can submit quotations."
        if self.rfq_id and self.rfq.buyer_id == self.supplier_id:
            errors["supplier"] = "The RFQ buyer cannot quote on their own RFQ."
        if self.rfq_id and self.rfq.status != RFQ.Status.OPEN:
            errors["rfq"] = "Quotations can only be submitted to open RFQs."
        if self.rfq_id and self.rfq.deadline <= timezone.now():
            errors["rfq"] = "Quotations cannot be submitted after the RFQ deadline."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Quotation for {self.rfq} by {self.supplier}"
