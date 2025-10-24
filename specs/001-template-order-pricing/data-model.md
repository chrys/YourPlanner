# Data Model: Template-First Order and Dynamic Pricing  # [added]

Date: 2025-10-21  # [added]

## Entities  # [added]

- Order  # [added]
  - Fields: id, customer_id, status (draft/confirmed), currency, total_amount, created_at, updated_at  # [added]
  - Relationships: belongs_to Customer; has_one TemplateComponent; has_many AddOnService, AddOnItem  # [added]
  - Rules: currency set by Template; total = template_total + sum(add-on subtotals)  # [added]

- TemplateComponent  # [added]
  - Fields: id, order_id (unique), template_id, guest_count, base_price, additional_guest_price, template_total  # [added]
  - Rules: template_total = base_price + additional_guest_price × max(0, guest_count - default_guests)  # [added]
  - Notes: services/items from template are locked (not persisted as editable lines)  # [added]

- AddOnService  # [added]
  - Fields: id, order_id, service_id, professional_id, service_price, subtotal  # [added]
  - Rules: subtotal = service_price + sum(child AddOnItemLine line_totals)  # [added]
  - Constraints: professional_id must match order.Template.professional_id  # [added]

- AddOnItemLine  # [added]
  - Fields: id, add_on_service_id (nullable for standalone items), item_id, unit_price, quantity, line_total  # [added]
  - Rules: line_total = unit_price × quantity; quantity within item min/max; active price in order currency  # [added]
  - Notes: For individual items not tied to a service, add_on_service_id is null  # [added]

## State Transitions  # [added]

- draft → confirmed (after verification/checkout)  # [added]
- Mutations allowed only in draft; recalc on each mutation  # [added]

## Validation Rules  # [added]

- Enforce same professional for add-ons  # [added]
- Enforce single order currency and active price availability  # [added]
- Enforce quantity bounds (min/max)  # [added]

