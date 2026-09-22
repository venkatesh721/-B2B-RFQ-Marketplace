# Demo Credentials (Assessment Only)

This file contains demo-only assessment credentials for the B2B RFQ Marketplace.
These accounts are for evaluation and demonstration purposes only and should not be used in production.

## Shared Demo Password

- Password for all demo users: `DemoPass@2026`

#mak

## Supplier Accounts

| Name | Email | Role | Password |
| --- | --- | --- | --- |
| Vikram Singh | supplier.demo.vikram@marketplace.in | Supplier | DemoPass@2026 |
| Meera Nair | supplier.demo.meera@marketplace.in | Supplier | DemoPass@2026 |
| Arjun Patel | supplier.demo.arjun@marketplace.in | Supplier | DemoPass@2026 |
| Rahul Kulkarni | supplier.demo.rahul@marketplace.in | Supplier | DemoPass@2026 |
| Sonali Desai | supplier.demo.sonali@marketplace.in | Supplier |   DemoPass@2026 |

## Example Workflow Tests

### Buyer workflow
- Log in as `buyer.demo.ananya@marketplace.in`.
- Create or view RFQs from the buyer dashboard.
- Confirm buyer can only access their own RFQs.
- Check that they can see quotations submitted on their RFQs.

### Supplier workflow
- Log in as `supplier.demo.vikram@marketplace.in`.
- Browse open RFQs from the supplier dashboard.
- Submit a quotation for an open RFQ.
- Confirm the supplier can only see their own quotations and cannot create RFQs.

## Notes

- All demo user passwords are hashed using Django's configured password hashing.
- The dataset is intentionally seeded in a safe, repeatable way and avoids duplicate demo records on reruns.
- Existing project data is not deleted by the seed command.
