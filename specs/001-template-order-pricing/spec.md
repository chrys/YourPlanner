# Feature Specification: Template-First Order and Dynamic Pricing  # [added]

**Feature Branch**: `[001-template-order-pricing]`  # [added]
**Created**: 2025-10-21  # [added]
**Status**: Draft  # [added]
**Input**: User description: "I need to change the orders Django app. The user can add three different entities in their Order. 1) The users initially must add a Template which has its own price = base_price + (additional_guest_price * additional guests), independent of prices of Services or Items it includes. The number of Items and Services of a Template cannot be changed or removed; only additional guests can be added causing price re-evaluation. 2) After the Template is added to the Basket, users can add Services (each with Items). Users can change quantity of each Item or remove them. 3) Users can also add individual Items and change quantity. Every time changes are made in the Order, users will verify changes and get the updated Total Price."  # [added]

## Clarifications  # [added]

### Session 2025-10-21  # [added]

- Q: Multiple templates per order? → A: One template per order.  # [added]
- Q: Order currency rules? → A: Single currency per order (template).  # [added]
- Q: Price frequency in totals? → A: One-time amounts only in basket total.  # [added]
- Q: Add-on Service pricing model? → A: Service.price + sum of Item line totals.  # [added]
- Q: Professional scope for add-ons? → A: Same professional as the Template.  # [added]

## User Scenarios & Testing *(mandatory)*  # [added]

### User Story 1 - Select Template and Set Guests (Priority: P1)  # [added]

Customers select a Template to start an order, set the number of guests, and add it  # [added]
to the basket. The Template price is computed as: base_price +  # [added]
(additional_guest_price × additional_guests). The Template’s included services/items  # [added]
are locked (not editable or removable).  # [added]

**Why this priority**: Establishes the required starting point for all orders and the  # [added]
correct pricing baseline.  # [added]

**Independent Test**: Choose a Template, set guests, verify order shows a Template  # [added]
line with the computed total and no ability to edit or remove included services/items.  # [added]

**Acceptance Scenarios**:  # [added]

1. Given no active order, When a user selects a Template and sets guests, Then a new  # [added]
   draft order is created with a Template line priced as per formula and the total  # [added]
   equals the Template price.  # [added]
2. Given an existing draft order without a Template, When a user adds a Template, Then  # [added]
   the order gains a Template line and the total equals the Template price.  # [added]
3. Given an order with a Template, When the user increases or decreases the guest  # [added]
   count within allowed bounds, Then the Template price recalculates and the order  # [added]
   total updates accordingly.  # [added]

---  # [added]

### User Story 2 - Add Services and Manage Their Items (Priority: P2)  # [added]

After adding a Template, customers add standalone Services. Each Service may include  # [added]
Items that the user can adjust or remove. These additions contribute to the order  # [added]
total independently of the Template’s fixed composition.  # [added]

**Why this priority**: Enables upsell and customization beyond the Template baseline.  # [added]

**Independent Test**: Add a Service with Items, change quantities/remove some, verify  # [added]
line totals and the updated order total (Template price + add‑ons).  # [added]

**Acceptance Scenarios**:  # [added]

1. Given an order with a Template, When a user adds a Service, Then a Service section  # [added]
   with its Items appears and contributes to the order total.  # [added]
2. Given a Service with Items in the order, When the user changes quantities or removes  # [added]
   an Item, Then the Service subtotal and the order total update immediately.  # [added]

---  # [added]

### User Story 3 - Add Individual Items (Priority: P3)  # [added]

Customers add individual Items directly to the order and adjust quantities. These  # [added]
items contribute to the total independently of the Template.  # [added]

**Why this priority**: Allows fine‑grained customization without adding full Services.  # [added]

**Independent Test**: Add an individual Item, change quantity, verify line totals and  # [added]
updated order total (Template price + add‑ons).  # [added]

**Acceptance Scenarios**:  # [added]

1. Given an order with a Template, When the user adds an Item and sets a quantity, Then  # [added]
   a line total appears and the order total increases accordingly.  # [added]
2. Given an added Item, When the user updates quantity to zero (or removes it), Then the  # [added]
   Item is removed and the order total decreases accordingly.  # [added]

### Edge Cases  # [updated]

- Template visibility or availability changes between browse and add → Show a clear  # [added]
  message and prevent add.  # [added]
- Guest count below minimum or above allowed maximum → Validate and block with guidance.  # [added]
- Attempt to edit or remove Template‑included services/items → Disallow with clear UI  # [added]
  message.  # [added]
- Currency mismatch between Template and add-ons → Disallow adding any add‑on without an  # [updated]
  active price in the order currency (order currency is set by the Template).  # [updated]
- Price frequency on add‑ons (one‑time vs recurring) → Only one‑time amounts contribute to  # [updated]
  the basket total; recurring amounts are shown as informational labels.  # [updated]

## Requirements *(mandatory)*  # [added]

### Functional Requirements  # [updated]

- **FR-001**: The system MUST require selection of a Template before any Services or  # [added]
  individual Items can be added to an order.  # [added]
- **FR-002**: The system MUST compute Template price as base_price +  # [added]
  (additional_guest_price × additional_guests) and update when guest count changes.  # [added]
- **FR-003**: The system MUST lock Template‑included services/items from user edits or  # [added]
  removal; only additional guests can be changed for the Template.  # [added]
- **FR-004**: The system MUST allow adding standalone Services after a Template is added,  # [added]
  and allow users to change/remove their Items and quantities.  # [added]
- **FR-005**: The system MUST allow adding individual Items with adjustable quantities.  # [added]
- **FR-006**: The system MUST present an updated order total after any change (Template  # [added]
  guests, add‑on Services/Items), and include a verification step summarizing changes.  # [added]
- **FR-007**: The system MUST display a clear price breakdown: Template component and  # [added]
  add‑on components with line totals and a grand total.  # [added]
- **FR-008**: The system MUST enforce quantity bounds (min/max) and availability for  # [added]
  all add‑on Items.  # [added]
- **FR-009**: The system MUST enforce a single order currency set by the Template; add‑ons  # [updated]
  MUST have an active price in that currency or be blocked from adding.  # [updated]
- **FR-011**: The system MUST show recurring prices as informational labels only; basket  # [added]
  totals include only one‑time amounts.  # [added]
- **FR-012**: For add‑on Services, the subtotal MUST equal Service.price plus the sum of  # [added]
  active Item line totals (quantity × item price) for that Service.  # [added]
- **FR-013**: The system MUST restrict add‑on Services and Items to the same Professional  # [added]
  as the order’s Template.  # [added]
- **FR-010**: The system MUST apply clear rounding rules and user‑visible amounts for all  # [added]
  displayed totals.  # [added]

### Key Entities *(include if feature involves data)*  # [added]

- **Order**: A draft/active order with a single required Template component and optional  # [added]
  add‑on Service/Item components.  # [added]
- **Template**: A curated bundle with base_price, additional_guest_price, default_guests;  # [added]
  includes fixed services/items that are not user‑editable.  # [added]
- **Service (add‑on)**: A standalone service the user can add post‑Template; contributes  # [added]
  a subtotal that includes a base Service.price plus its items and their quantities.  # [updated]
- **Item (add‑on)**: An individual item the user can add directly with quantity.  # [added]
- **Price**: Active price for add‑on Items (and/or Services where applicable), possibly  # [added]
  with frequency and constraints.  # [added]

## Success Criteria *(mandatory)*  # [added]

### Measurable Outcomes  # [added]

- **SC-001**: 95% of orders show correct totals across at least 5 change sequences  # [added]
  (guest changes, add/remove service/item) verified in acceptance tests.  # [added]
- **SC-002**: Median time to add a Template and verify total ≤ 30 seconds in a  # [added]
  representative test.  # [added]
- **SC-003**: 0 critical calculation defects during a 2‑week stabilization period post  # [added]
  launch; <1% basket recalculation errors.  # [added]
- **SC-004**: 90% of test participants successfully complete Template selection and add  # [added]
  at least one add‑on without assistance.  # [added]

### Assumptions  # [updated]

- Exactly one Template per order; users may create multiple orders if they need multiple  # [updated]
  Templates.  # [updated]
- Add‑on Service and Item prices are treated as one‑time amounts for the basket total;  # [updated]
  recurring fees are displayed but excluded from the total.  # [updated]

