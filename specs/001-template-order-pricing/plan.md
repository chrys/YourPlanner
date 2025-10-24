# Implementation Plan: Template-First Order and Dynamic Pricing  # [added]

**Branch**: `001-template-order-pricing` | **Date**: 2025-10-21 | **Spec**: /Users/chrys/Projects/YourPlanner/specs/001-template-order-pricing/spec.md  # [added]
**Input**: Feature specification from `/specs/001-template-order-pricing/spec.md`  # [added]

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary  # [added]

Implement a template‑first ordering flow where each order begins with exactly one  # [added]
Template priced as base_price + (additional_guest_price × additional_guests). Template  # [added]
composition is locked (services/items not editable). After the Template, users can add  # [added]
add‑on Services (subtotal = Service.price + sum of item lines) and individual Items.  # [added]
Totals update immediately; order currency is set by the Template and enforced for add‑ons.  # [added]

## Technical Context  # [added]

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.x (Django project)  # [added]
**Primary Dependencies**: Django, pytest/pytest‑django, Playwright (UI smoke)  # [added]
**Storage**: sqlite3 locally; PostgreSQL in staging/production  # [added]
**Testing**: pytest with coverage ≥85%; deterministic tests; Playwright smoke  # [added]
**Target Platform**: Linux server behind Nginx → Gunicorn → Django  # [added]
**Project Type**: Web application (Django monorepo with multiple apps)  # [added]
**Performance Goals**: Basket recalculation perceived instant (<300ms p95 server time)  # [added]
**Constraints**: Single currency per order (from Template); same‑professional add‑ons  # [added]
**Scale/Scope**: MVP scope—Templates, add‑on Services/Items, basket verify/update  # [added]

## Constitution Check  # [added]

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Merge‑blocking gates from constitution:  # [added]
- Formatting/Linting: black --check; ruff; isort --check‑only  # [added]
- Type checking: mypy (migrations excluded)  # [added]
- Tests: pytest; coverage ≥85% overall and per‑package minima  # [added]
- UI Smoke: Playwright (register, login, create order)  # [added]
- Security: Bandit; Gitleaks (0 high/critical)  # [added]

Status: No planned violations. Tests and coverage to be added/updated with the feature.  # [added]

## Project Structure  # [added]

### Documentation (this feature)  # [added]

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)  # [added]
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
apps/
├── templates/              # Template models/views/templates (curated bundles)
├── orders/                 # Basket/order models, views, templates
├── services/               # Services, Items, Prices
└── core/, users/, labels/, rules/ ...

specs/001-template-order-pricing/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
```

**Structure Decision**: Use existing Django apps; extend orders to support Template  # [added]
component plus add‑on Services/Items with recalculation and verification steps.  # [added]

## Complexity Tracking  # [added]

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |  # [added]

