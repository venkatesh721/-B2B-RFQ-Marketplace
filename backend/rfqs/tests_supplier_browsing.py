from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import RFQ


class SupplierRFQBrowsingTests(APITestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email="buyer@example.com", password="SecurePass123!", name="Buyer", role=User.Role.BUYER
        )
        self.supplier = User.objects.create_user(
            email="supplier@example.com", password="SecurePass123!", name="Supplier", role=User.Role.SUPPLIER
        )
        self.list_url = reverse("rfq-list")

    def create_rfq(self, *, name="Steel bolts", location="Mumbai", deadline=None):
        return RFQ.objects.create(
            buyer=self.buyer,
            product_or_service_name=name,
            requirement_description="Industrial requirement",
            quantity=100,
            delivery_location=location,
            deadline=deadline or timezone.now() + timedelta(days=7),
        )

    def test_supplier_can_list_available_rfqs_without_buyer_data(self):
        self.create_rfq()
        self.client.force_authenticate(self.supplier)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertNotIn("buyer", response.data["results"][0])

    def test_supplier_can_search_rfqs(self):
        self.create_rfq(name="Steel bolts")
        self.create_rfq(name="Office chairs")
        self.client.force_authenticate(self.supplier)

        response = self.client.get(self.list_url, {"search": "steel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["product_or_service_name"], "Steel bolts")

    def test_supplier_can_view_available_rfq_details(self):
        rfq = self.create_rfq(name="Steel bolts")
        self.client.force_authenticate(self.supplier)

        response = self.client.get(reverse("rfq-detail", args=[rfq.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["requirement_description"], "Industrial requirement")
        self.assertNotIn("buyer", response.data)

    def test_supplier_can_filter_by_product_and_location(self):
        self.create_rfq(name="Steel bolts", location="Mumbai")
        self.create_rfq(name="Steel sheets", location="Delhi")
        self.client.force_authenticate(self.supplier)

        response = self.client.get(
            self.list_url,
            {"product_or_service_name": "bolt", "delivery_location": "mumbai"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_supplier_results_are_paginated(self):
        for number in range(11):
            self.create_rfq(name=f"Item {number}")
        self.client.force_authenticate(self.supplier)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 11)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_supplier_does_not_see_expired_rfqs(self):
        self.create_rfq(name="Active item")
        expired = self.create_rfq(name="Expired item", deadline=timezone.now() - timedelta(days=1))
        self.client.force_authenticate(self.supplier)

        response = self.client.get(self.list_url)
        detail_response = self.client.get(reverse("rfq-detail", args=[expired.id]))

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_browse_rfqs(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
