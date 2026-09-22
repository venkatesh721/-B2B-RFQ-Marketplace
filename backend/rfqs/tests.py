from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import RFQ


class BuyerRFQAPITests(APITestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            password="SecurePass123!",
            name="Buyer One",
            role=User.Role.BUYER,
        )
        self.other_buyer = User.objects.create_user(
            email="other-buyer@example.com",
            password="SecurePass123!",
            name="Buyer Two",
            role=User.Role.BUYER,
        )
        self.supplier = User.objects.create_user(
            email="supplier@example.com",
            password="SecurePass123!",
            name="Supplier One",
            role=User.Role.SUPPLIER,
        )
        self.list_url = reverse("rfq-list")

    def valid_payload(self):
        return {
            "product_or_service_name": "Steel bolts",
            "requirement_description": "Need industrial-grade M8 bolts.",
            "quantity": 500,
            "delivery_location": "Mumbai",
            "deadline": (timezone.now() + timedelta(days=7)).isoformat(),
        }

    def create_rfq(self, buyer=None):
        return RFQ.objects.create(
            buyer=buyer or self.buyer,
            product_or_service_name="Steel bolts",
            requirement_description="Need industrial-grade M8 bolts.",
            quantity=500,
            delivery_location="Mumbai",
            deadline=timezone.now() + timedelta(days=7),
        )

    def test_buyer_can_create_rfq(self):
        self.client.force_authenticate(self.buyer)

        response = self.client.post(self.list_url, self.valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["buyer"], self.buyer.id)
        self.assertEqual(RFQ.objects.count(), 1)

    def test_creation_rejects_invalid_input(self):
        self.client.force_authenticate(self.buyer)
        payload = self.valid_payload()
        payload["quantity"] = 0
        payload["deadline"] = (timezone.now() - timedelta(days=1)).isoformat()

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertIn("deadline", response.data)

    def test_unauthenticated_user_cannot_create_rfq(self):
        response = self.client.post(self.list_url, self.valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_cannot_create_rfq(self):
        self.client.force_authenticate(self.supplier)

        response = self.client.post(self.list_url, self.valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_cannot_edit_another_buyers_rfq(self):
        rfq = self.create_rfq(buyer=self.other_buyer)
        self.client.force_authenticate(self.buyer)

        response = self.client.patch(
            reverse("rfq-detail", args=[rfq.id]),
            {"quantity": 600},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        rfq.refresh_from_db()
        self.assertEqual(rfq.quantity, 500)

    def test_buyer_can_delete_own_rfq(self):
        rfq = self.create_rfq()
        self.client.force_authenticate(self.buyer)

        response = self.client.delete(reverse("rfq-detail", args=[rfq.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RFQ.objects.filter(id=rfq.id).exists())

    def test_buyer_only_sees_and_retrieves_own_rfqs(self):
        own_rfq = self.create_rfq()
        other_rfq = self.create_rfq(buyer=self.other_buyer)
        self.client.force_authenticate(self.buyer)

        list_response = self.client.get(self.list_url)
        own_detail = self.client.get(reverse("rfq-detail", args=[own_rfq.id]))
        other_detail = self.client.get(reverse("rfq-detail", args=[other_rfq.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["id"], own_rfq.id)
        self.assertEqual(own_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(other_detail.status_code, status.HTTP_403_FORBIDDEN)

    def test_rfq_creation_rejects_missing_required_fields(self):
        self.client.force_authenticate(self.buyer)
        payload = self.valid_payload()
        del payload["product_or_service_name"]

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("product_or_service_name", response.data)
