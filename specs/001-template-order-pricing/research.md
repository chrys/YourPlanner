# Research: Template-First Order and Dynamic Pricing  # [added]

Date: 2025-10-21  # [added]
Branch: 001-template-order-pricing  # [added]

## Decisions  # [added]

- Decision: One Template per order  # [added]
  - Rationale: Simplifies composition, pricing, and UI; users can create multiple orders if needed  # [added]
  - Alternatives: Multiple Templates per order with combined guests (rejected: higher complexity)  # [added]

- Decision: Single currency per order (from Template)  # [added]
  - Rationale: Avoids conversion/rounding errors; consistent UX  # [added]
  - Alternatives: Auto-convert add-ons (rejected: requires FX source, drift risk)  # [added]

- Decision: Basket total uses one-time amounts only  # [added]
  - Rationale: Keeps basket total clear; recurring fees shown as info labels  # [added]
  - Alternatives: Include first billing cycle (rejected: confusing)  # [added]

- Decision: Add-on Service pricing = Service.price + sum(item lines)  # [added]
  - Rationale: Supports baseline service fee plus configurable items  # [added]
  - Alternatives: Only service.price; only items; per-service mode switch  # [added]

- Decision: Add-ons restricted to same Professional as Template  # [added]
  - Rationale: Simplifies fulfillment and avoids cross-vendor conflicts  # [added]
  - Alternatives: Multi-vendor basket; regional constraints  # [added]

## Best Practices  # [added]

- Django totals: persist snapshot amounts for order lines; compute grand total with precise Decimal  # [added]
- Concurrency: use select_for_update during recalculation on POST mutations  # [added]
- Validation: enforce quantity bounds; block add-ons without active price in order currency  # [added]
- UX: confirmation banner for recalculations; disable double-submit; show loading indicator >300ms  # [added]

## Open Questions (none blocking)  # [added]

- Out-of-scope declaration candidates to list in plan (payments, shipping, etc.)  # [added]
