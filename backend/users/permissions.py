"""Reusable authorization rules for the marketplace API views."""

from django.utils import timezone
from rest_framework.permissions import BasePermission

from rfqs.models import RFQ
from users.models import User


def visible_rfqs_for(user):
    """Return only the RFQs that a user is allowed to see in a list view."""
    if not user.is_authenticated:
        return RFQ.objects.none()
    if user.role == User.Role.BUYER:
        return RFQ.objects.filter(buyer=user)
    if user.role == User.Role.SUPPLIER:
        return RFQ.objects.filter(
            status=RFQ.Status.OPEN,
            deadline__gt=timezone.now(),
        )
    return RFQ.objects.none()


class IsBuyer(BasePermission):
    message = "Only buyers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.BUYER
        )


class IsSupplier(BasePermission):
    message = "Only suppliers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.SUPPLIER
        )


class IsBuyerOrSupplier(BasePermission):
    message = "Only buyers or suppliers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.Role.BUYER, User.Role.SUPPLIER)
        )


class IsRFQBuyer(IsBuyer):
    """Allows an RFQ change only to its owning buyer."""

    message = "Only the buyer who created this RFQ can change it."

    def has_object_permission(self, request, view, obj):
        return obj.buyer_id == request.user.id


class CanViewRFQ(BasePermission):
    """Buyers see their RFQs; suppliers can view available RFQs."""

    message = "You do not have permission to view this RFQ."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.BUYER:
            return obj.buyer_id == request.user.id
        if request.user.role == User.Role.SUPPLIER:
            return obj.status == RFQ.Status.OPEN and obj.deadline > timezone.now()
        return False


class CanSubmitQuotation(IsSupplier):
    """Allows a supplier to quote only an open RFQ before its deadline."""

    message = "Suppliers can quote only open RFQs before their deadline."

    def has_object_permission(self, request, view, obj):
        return (
            obj.status == RFQ.Status.OPEN
            and obj.deadline > timezone.now()
            and obj.buyer_id != request.user.id
        )


class IsQuotationSupplier(IsSupplier):
    """Allows quotation changes only to the supplier who submitted it."""

    message = "Only the supplier who submitted this quotation can change it."

    def has_object_permission(self, request, view, obj):
        return obj.supplier_id == request.user.id


class IsSelf(BasePermission):
    """Use on private User detail views to stop access to another user."""

    message = "You can only access your own user data."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
