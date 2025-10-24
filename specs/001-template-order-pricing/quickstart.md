# Basket Flow Quickstart <!-- [modified] -->

This guide shows how to use the Template-First Basket flow to build an order. <!-- [modified] -->
<!-- API endpoints have been removed from the project for now; this Quickstart focuses on flow/behavior rather than HTTP calls. [added] -->

## Flow overview <!-- [added] -->
1) Create or fetch draft basket (session-based) <!-- [added] -->
2) Select a Template with guest_count (sets currency and template subtotal) <!-- [added] -->
3) Add add-on Services and their Items (same Professional and currency) <!-- [added] -->
4) Optionally add standalone Items (same currency) <!-- [added] -->
5) Verify basket to recompute totals and validate before checkout <!-- [added] -->

## Integration note (API deferred) <!-- [added] -->
<!-- Previous HTTP endpoint list removed because API routes are disabled. [added] -->
The basket feature will initially be integrated via existing Django views/forms. The API contract is retained as a draft for future work.

Refer to `contracts/openapi.yaml` for the draft Basket data model (status: draft; API disabled). <!-- [modified] -->

## Example sequence (UI/server-side) <!-- [modified] -->
<!-- Replaced curl-based API examples with UI/server-side flow because API is disabled. [added] -->
1) Customer selects a Template and enters guest_count.
2) System computes template subtotal = base_price + max(0, guests - default_guests) * price_per_additional_guest.
3) Customer adds add-on Services restricted to the same Professional; each service subtotal = service.price + sum(item line subtotals).
4) Customer optionally adds standalone Items priced in the order currency.
5) System verifies basket and displays totals: template_total + services_total + items_total; recurring_total displayed separately.

## Validation rules (excerpt) <!-- [added] -->
- One template per order; selecting a new one replaces the previous. <!-- [added] -->
- Order currency is set by template; add-ons must price in that currency. <!-- [added] -->
- Only one-time amounts are included in `totals.grand_total`; recurring totals are informational. <!-- [added] -->
- Add-on service subtotal = service.price + sum(item line subtotals). <!-- [added] -->
- Add-ons restricted to same Professional as the template's Professional. <!-- [added] -->
