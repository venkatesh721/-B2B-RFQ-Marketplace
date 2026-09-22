from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rfqs.models import Quotation, RFQ

from .models import User


class AuthenticationAPITests(APITestCase):
    def register_payload(self, **overrides):
        payload = {
            "name": "Buyer One",
            "email": "buyer@example.com",
            "password": "SecurePass123!",
            "role": User.Role.BUYER,
        }
        payload.update(overrides)
        return payload

    def test_registers_user_with_hashed_password_and_safe_response(self):
        response = self.client.post(reverse("register"), self.register_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        user = User.objects.get(email="buyer@example.com")
        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertNotEqual(user.password, "SecurePass123!")

    def test_registration_rejects_duplicate_email_and_weak_password(self):
        self.client.post(reverse("register"), self.register_payload(), format="json")

        duplicate = self.client.post(reverse("register"), self.register_payload(), format="json")
        weak = self.client.post(
            reverse("register"), self.register_payload(email="new@example.com", password="short"), format="json"
        )

        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", duplicate.data)
        self.assertEqual(weak.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", weak.data)

    def test_login_returns_jwts_and_me_requires_valid_authentication(self):
        User.objects.create_user(**self.register_payload())

        unauthenticated = self.client.get(reverse("me"))
        login = self.client.post(
            reverse("login"), {"email": "buyer@example.com", "password": "SecurePass123!"}, format="json"
        )

        self.assertEqual(unauthenticated.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)
        self.assertNotIn("password", login.data["user"])

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        me = self.client.get(reverse("me"))
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], "buyer@example.com")


class DemoSeedDataTests(APITestCase):
    def test_seed_demo_data_creates_realistic_dataset_without_duplicates(self):
        call_command("seed_demo_data")
        call_command("seed_demo_data")

        demo_buyers = User.objects.filter(email__startswith="buyer.demo.")
        demo_suppliers = User.objects.filter(email__startswith="supplier.demo.")

        self.assertEqual(demo_buyers.count(), 5)
        self.assertEqual(demo_suppliers.count(), 5)
        self.assertGreaterEqual(RFQ.objects.filter(buyer__email__startswith="buyer.demo.").count(), 12)
        self.assertLessEqual(RFQ.objects.filter(buyer__email__startswith="buyer.demo.").count(), 15)
        self.assertGreaterEqual(Quotation.objects.filter(supplier__email__startswith="supplier.demo.").count(), 20)
        self.assertLessEqual(Quotation.objects.filter(supplier__email__startswith="supplier.demo.").count(), 25)

        self.assertTrue(RFQ.objects.filter(status=RFQ.Status.OPEN, buyer__email__startswith="buyer.demo.").exists())
        self.assertTrue(RFQ.objects.filter(status=RFQ.Status.CLOSED, buyer__email__startswith="buyer.demo.").exists())

        buyer = demo_buyers.first()
        self.assertTrue(RFQ.objects.filter(buyer=buyer).exists())
