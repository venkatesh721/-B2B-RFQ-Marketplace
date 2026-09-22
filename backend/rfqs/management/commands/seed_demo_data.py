from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rfqs.models import Quotation, RFQ
from users.models import User


DEMO_PASSWORD = "DemoPass@2026"


class Command(BaseCommand):
    help = "Create realistic, repeatable B2B demo data for the RFQ marketplace."

    def handle(self, *args, **options):
        now = timezone.now()

        demo_buyer_emails = [
            "buyer.demo.ananya@marketplace.in",
            "buyer.demo.rohan@marketplace.in",
            "buyer.demo.kavya@marketplace.in",
            "buyer.demo.nikhil@marketplace.in",
            "buyer.demo.pooja@marketplace.in",
        ]
        demo_supplier_emails = [
            "supplier.demo.vikram@marketplace.in",
            "supplier.demo.meera@marketplace.in",
            "supplier.demo.arjun@marketplace.in",
            "supplier.demo.rahul@marketplace.in",
            "supplier.demo.sonali@marketplace.in",
        ]

        RFQ.objects.filter(buyer__email__startswith="buyer.demo.").delete()
        Quotation.objects.filter(supplier__email__startswith="supplier.demo.").delete()
        User.objects.filter(email__startswith="buyer.demo.").delete()
        User.objects.filter(email__startswith="supplier.demo.").delete()

        buyer_records = [
            ("buyer.demo.ananya@marketplace.in", "Ananya Sharma"),
            ("buyer.demo.rohan@marketplace.in", "Rohan Mehta"),
            ("buyer.demo.kavya@marketplace.in", "Kavya Iyer"),
            ("buyer.demo.nikhil@marketplace.in", "Nikhil Rao"),
            ("buyer.demo.pooja@marketplace.in", "Pooja Kulkarni"),
        ]
        supplier_records = [
            ("supplier.demo.vikram@marketplace.in", "Vikram Singh"),
            ("supplier.demo.meera@marketplace.in", "Meera Nair"),
            ("supplier.demo.arjun@marketplace.in", "Arjun Patel"),
            ("supplier.demo.rahul@marketplace.in", "Rahul Kulkarni"),
            ("supplier.demo.sonali@marketplace.in", "Sonali Desai"),
        ]

        buyers = self._ensure_users(buyer_records, User.Role.BUYER)
        suppliers = self._ensure_users(supplier_records, User.Role.SUPPLIER)

        rfq_specs = [
            (
                buyers[0],
                "Industrial LED High-Bay Lights",
                "Supply 120 energy-efficient 150W LED high-bay fixtures for a warehouse with mounting brackets, emergency backup options, and minimum 3-year warranty coverage.",
                120,
                "Bhiwandi, Maharashtra",
                now + timedelta(days=12),
                RFQ.Status.OPEN,
            ),
            (
                buyers[0],
                "Warehouse Inventory Management Software",
                "Deploy a cloud-based inventory and warehouse management system across three locations, with stock movement tracking, barcode integration, and onboarding support for a 40-user team.",
                1,
                "Pune, Maharashtra",
                now + timedelta(days=24),
                RFQ.Status.OPEN,
            ),
            (
                buyers[0],
                "Stainless Steel Storage Racks",
                "Need 32 heavy-duty stainless steel storage racks for a food processing unit with modular shelving, anti-corrosion coating, and anchor fittings.",
                32,
                "Ahmedabad, Gujarat",
                now + timedelta(days=18),
                RFQ.Status.OPEN,
            ),
            (
                buyers[1],
                "Ergonomic Office Workstations",
                "Procure modular workstations and ergonomic chairs for 75 seats in a new operations centre, including cable trays, drawers, and assembly support.",
                75,
                "Whitefield, Bengaluru",
                now + timedelta(days=21),
                RFQ.Status.OPEN,
            ),
            (
                buyers[1],
                "UPS Battery Backup Systems",
                "Requirement for 40 kVA and 60 kVA three-phase UPS systems for a data centre with battery banks, commissioning, and maintenance support.",
                2,
                "Andheri East, Mumbai",
                now - timedelta(days=3),
                RFQ.Status.CLOSED,
            ),
            (
                buyers[1],
                "Managed IT Helpdesk Services",
                "Need managed endpoint support and service desk coverage for 250 users, including remote troubleshooting, ticketing, and SLA reporting for 12 months.",
                1,
                "Hyderabad, Telangana",
                now + timedelta(days=26),
                RFQ.Status.OPEN,
            ),
            (
                buyers[2],
                "Five-Ply Corrugated Packaging Boxes",
                "Custom printed five-ply cartons for consumer electronics accessories; must handle up to 12 kg and include month-wise dispatch to multiple warehouses.",
                18000,
                "Sanand, Gujarat",
                now + timedelta(days=14),
                RFQ.Status.OPEN,
            ),
            (
                buyers[2],
                "Conference Room AV Equipment",
                "Supply a 12-seat boardroom package consisting of 75-inch displays, video conferencing kit, wireless mics, and ceiling audio for hybrid meetings.",
                1,
                "Koramangala, Bengaluru",
                now - timedelta(days=7),
                RFQ.Status.CLOSED,
            ),
            (
                buyers[2],
                "Industrial Fasteners and Washers",
                "Source M8 and M10 stainless steel bolts, nuts, and washers to ISO 3506 and provide batch certificates, packing lists, and prompt dispatch.",
                25000,
                "Chennai, Tamil Nadu",
                now + timedelta(days=17),
                RFQ.Status.OPEN,
            ),
            (
                buyers[3],
                "CNC Machine Maintenance Services",
                "Annual preventive maintenance and tooling calibration for vertical machining centres used in precision component production.",
                6,
                "Pimpri Chinchwad, Maharashtra",
                now + timedelta(days=19),
                RFQ.Status.OPEN,
            ),
            (
                buyers[3],
                "Plastic Injection Mould Tooling",
                "Require tooling for 2-part plastic cover components used in consumer appliances; include prototype validation and QA documentation.",
                2,
                "Coimbatore, Tamil Nadu",
                now + timedelta(days=30),
                RFQ.Status.OPEN,
            ),
            (
                buyers[3],
                "Thermal Shipping Labels",
                "Need direct thermal barcode labels for Zebra printers, with 100x150 mm size, permanent adhesive, and monthly supply of 50,000 labels.",
                50000,
                "Noida, Uttar Pradesh",
                now + timedelta(days=15),
                RFQ.Status.OPEN,
            ),
            (
                buyers[4],
                "Microprocessor Control Panels",
                "Supply PLC-based control panels for packaging automation with HMI display, DIN rail components, and panel wiring documentation.",
                12,
                "Vapi, Gujarat",
                now + timedelta(days=22),
                RFQ.Status.OPEN,
            ),
            (
                buyers[4],
                "Water Treatment Chemicals",
                "Need caustic soda and anti-scalant chemicals for a cooling loop and boiler treatment program with 6-month supply schedule and MSDS support.",
                2500,
                "Jaipur, Rajasthan",
                now - timedelta(days=14),
                RFQ.Status.CLOSED,
            ),
        ]

        rfqs = []
        for buyer, name, description, quantity, location, deadline, status in rfq_specs:
            rfq, _ = RFQ.objects.get_or_create(
                buyer=buyer,
                product_or_service_name=name,
                defaults={
                    "requirement_description": description,
                    "quantity": quantity,
                    "delivery_location": location,
                    "deadline": deadline,
                    "status": status,
                },
            )
            if rfq.requirement_description != description or rfq.quantity != quantity or rfq.delivery_location != location:
                rfq.requirement_description = description
                rfq.quantity = quantity
                rfq.delivery_location = location
                rfq.deadline = deadline
                rfq.status = status
                rfq.save()
            rfqs.append(rfq)

        quote_specs = [
            (rfqs[0], suppliers[0], "238500.00", "10 business days", "BIS-compliant LED fixtures with installation support available across Maharashtra."),
            (rfqs[0], suppliers[3], "246000.00", "12 business days", "Includes mounting hardware, surge protection, and a three-year replacement warranty."),
            (rfqs[1], suppliers[1], "965000.00", "6 weeks", "Includes discovery workshops, integrations, training, and one year of post-go-live support."),
            (rfqs[1], suppliers[2], "1025000.00", "5 weeks", "Warehouse implementation package with mobility features and API integration for ERP and WMS."),
            (rfqs[2], suppliers[4], "428000.00", "14 business days", "Stainless racks with anti-corrosive treatment and anchor fittings for food-grade environments."),
            (rfqs[2], suppliers[1], "460000.00", "18 business days", "Custom modular shelving and freight-ready packing support for industrial dispatch operations."),
            (rfqs[3], suppliers[2], "712500.00", "15 business days", "Laminate finish options and a post-installation service visit are included in this proposal."),
            (rfqs[3], suppliers[0], "748000.00", "18 business days", "Ergonomic seating and workstation assembly included in the commercial package."),
            (rfqs[5], suppliers[4], "342000.00", "21 business days", "We provide a 24x7 service desk, endpoint support, and SLA-based ticket resolution for 250 users."),
            (rfqs[5], suppliers[2], "365000.00", "20 business days", "Support package includes remote monitoring, user onboarding, and monthly service reviews."),
            (rfqs[6], suppliers[3], "414000.00", "9 business days", "Food-grade kraft board, two-colour printing, and staggered dispatch to multiple warehouse locations."),
            (rfqs[6], suppliers[1], "432000.00", "11 business days", "Includes one artwork revision and palletised delivery in monthly batches to Sanand."),
            (rfqs[8], suppliers[0], "287500.00", "14 business days", "ISO 3506 material certificates and batch traceability will be provided with each shipment."),
            (rfqs[8], suppliers[2], "275000.00", "12 business days", "Ready stock for standard sizes; sample lot can be dispatched before the purchase order."),
            (rfqs[9], suppliers[4], "1685000.00", "20 days", "Annual preventive maintenance contract covering spindle testing, calibration, and priority support."),
            (rfqs[9], suppliers[3], "1750000.00", "18 days", "Dedicated maintenance engineer and tool-life benchmarking are included for six machines."),
            (rfqs[10], suppliers[1], "1250000.00", "8 weeks", "Prototype trials, tool validation, and process inspection support included with tooling development."),
            (rfqs[10], suppliers[0], "1185000.00", "7 weeks", "Includes QC documentation and sampling support for consumer appliance component runs."),
            (rfqs[11], suppliers[3], "315000.00", "8 business days", "Premium direct thermal labels supplied in 1,000-label rolls with core size matched to Zebra printers."),
            (rfqs[11], suppliers[4], "329000.00", "10 business days", "Includes overprint support and monthly replenishment plan for warehouse barcode operations."),
            (rfqs[12], suppliers[0], "845000.00", "18 business days", "PLC control panels with HMI display, panel wiring, and FAT testing support for packaging automation."),
            (rfqs[12], suppliers[2], "890000.00", "16 business days", "Includes custom enclosure design, autopower configuration, and installation documentation."),
        ]

        with transaction.atomic():
            for rfq, supplier, price, delivery, message in quote_specs:
                Quotation.objects.get_or_create(
                    rfq=rfq,
                    supplier=supplier,
                    defaults={
                        "quoted_price": Decimal(price),
                        "estimated_delivery_time": delivery,
                        "message": message,
                    },
                )

        total_buyers = User.objects.filter(role=User.Role.BUYER).count()
        total_suppliers = User.objects.filter(role=User.Role.SUPPLIER).count()
        total_rfqs = RFQ.objects.count()
        total_quotes = Quotation.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data created successfully: {total_buyers} buyers, {total_suppliers} suppliers, "
                f"{total_rfqs} RFQs, and {total_quotes} quotations. "
                f"Demo password: {DEMO_PASSWORD}"
            )
        )

    def _ensure_users(self, records, role):
        users = []
        for email, name in records:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"name": name, "role": role},
            )
            user.name = name
            user.role = role
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["name", "role", "password"])
            users.append(user)
        return users
