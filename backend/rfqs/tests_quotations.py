from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Quotation, RFQ


class QuotationAPITests(APITestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email="buyer@example.com", password="SecurePass123!", name="Buyer", role=User.Role.BUYER
        )
        self.other_buyer = User.objects.create_user(
            email="other-buyer@example.com", password="SecurePass123!", name="Other Buyer", role=User.Role.BUYER
        )
        self.supplier = User.objects.create_user(
            email="supplier@example.com", password="SecurePass123!", name="Supplier", role=User.Role.SUPPLIER
        )
        self.other_supplier = User.objects.create_user(
            email="other-supplier@example.com", password="SecurePass123!", name="Other Supplier", role=User.Role.SUPPLIER
        )
        self.rfq = self.create_rfq()
        self.quote_url = reverse("quotation-list")

    def create_rfq(self, buyer=None, deadline=None, status_value=RFQ.Status.OPEN):
        return RFQ.objects.create(
            buyer=buyer or self.buyer,
            product_or_service_name="Steel bolts",
            requirement_description="Industrial-grade M8 bolts",
            quantity=500,
            delivery_location="Mumbai",
            deadline=deadline or timezone.now() + timedelta(days=7),
            status=status_value,
        )

    def payload(self, rfq=None, **overrides):
        data = {
            "rfq": (rfq or self.rfq).id,
            "quoted_price": "12500.00",
            "estimated_delivery_time": "5 business days",
            "message": "We can meet the requested specification.",
        }
        data.update(overrides)
        return data

    def create_quote(self, supplier=None, rfq=None):
        return Quotation.objects.create(
            supplier=supplier or self.supplier,
            rfq=rfq or self.rfq,
            quoted_price="12500.00",
            estimated_delivery_time="5 business days",
            message="Available",
        )

    def test_supplier_can_submit_quotation(self):
        self.client.force_authenticate(self.supplier)

        response = self.client.post(self.quote_url, self.payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["supplier"], self.supplier.id)
        self.assertEqual(Quotation.objects.filter(rfq=self.rfq, supplier=self.supplier).count(), 1)

    def test_only_authenticated_suppliers_can_submit(self):
        self.assertEqual(self.client.post(self.quote_url, self.payload(), format="json").status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.post(self.quote_url, self.payload(), format="json").status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_rejects_invalid_rfq_price_and_duplicate(self):
        self.client.force_authenticate(self.supplier)
        self.assertIn("quoted_price", self.client.post(
            self.quote_url, self.payload(quoted_price="0"), format="json"
        ).data)

        expired_rfq = self.create_rfq(deadline=timezone.now() - timedelta(minutes=1))
        self.assertIn("rfq", self.client.post(self.quote_url, self.payload(rfq=expired_rfq), format="json").data)

        closed_rfq = self.create_rfq(status_value=RFQ.Status.CLOSED)
        self.assertIn("rfq", self.client.post(self.quote_url, self.payload(rfq=closed_rfq), format="json").data)

        self.create_quote()
        duplicate_response = self.client.post(self.quote_url, self.payload(), format="json")
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rfq", duplicate_response.data)

    def test_submission_rejects_missing_required_fields(self):
        self.client.force_authenticate(self.supplier)
        payload = self.payload()
        del payload["estimated_delivery_time"]

        response = self.client.post(self.quote_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("estimated_delivery_time", response.data)

    def test_supplier_can_only_view_own_quotations(self):
        own_quote = self.create_quote()
        other_quote = self.create_quote(supplier=self.other_supplier)
        self.client.force_authenticate(self.supplier)

        response = self.client.get(reverse("quotation-my"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([quote["id"] for quote in response.data], [own_quote.id])
        self.assertNotIn(other_quote.id, [quote["id"] for quote in response.data])

    def test_only_owning_buyer_can_view_rfq_quotations(self):
        quote = self.create_quote()
        quote_url = reverse("rfq-quotations", args=[self.rfq.id])
        self.client.force_authenticate(self.buyer)

        response = self.client.get(quote_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], quote.id)

        self.client.force_authenticate(self.other_buyer)
        self.assertEqual(self.client.get(quote_url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.supplier)
        self.assertEqual(self.client.get(quote_url).status_code, status.HTTP_403_FORBIDDEN)
