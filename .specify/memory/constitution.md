<!--
Sync Impact Report  <!-- [updated] -->
- Version change: unknown → 1.0.0  <!-- [updated] -->
- Modified principles:  <!-- [updated] -->
	- [PRINCIPLE_1_NAME] → Code Quality and Consistency  <!-- [updated] -->
	- [PRINCIPLE_2_NAME] → Test Discipline and Coverage  <!-- [updated] -->
	- [PRINCIPLE_3_NAME] → UX Consistency and Accessibility  <!-- [updated] -->
	- [PRINCIPLE_4_NAME] → Performance and Efficiency  <!-- [updated] -->
	- [PRINCIPLE_5_NAME] → Security and Observability  <!-- [updated] -->
- Added sections: Technology Stack and Environments; Development Workflow and Quality Gates  <!-- [updated] -->
- Removed sections: None  <!-- [updated] -->
- Templates requiring updates:  <!-- [updated] -->
	- .specify/templates/plan-template.md → ✅ aligned (Constitution Check reads gates)  <!-- [updated] -->
	- .specify/templates/spec-template.md → ✅ aligned (no agent-specific references)  <!-- [updated] -->
	- .specify/templates/tasks-template.md → ✅ aligned (task categories map to principles)  <!-- [updated] -->
	- .specify/templates/commands/* → ⚠ pending (folder not present in repo)  <!-- [updated] -->
- Deferred TODOs:  <!-- [updated] -->
	- TODO(RATIFICATION_DATE): Original adoption date unknown; set when known  <!-- [updated] -->
-->

# YourPlanner Constitution  <!-- [updated] -->
<!-- Project constitution for a Django web application -->  <!-- [updated] -->

## Core Principles  <!-- [updated] -->

### Code Quality and Consistency  <!-- [updated] -->
Code MUST be consistently formatted and linted. Python uses black for formatting,  <!-- [updated] -->
ruff for linting, and isort for import ordering. Public functions, serializers, and  <!-- [updated] -->
utilities MUST include type annotations and pass mypy; migrations are excluded.  <!-- [updated] -->
Security hygiene is mandatory: no secrets in VCS; Bandit and Gitleaks MUST pass  <!-- [updated] -->
with zero high/critical findings.  <!-- [updated] -->

### Test Discipline and Coverage  <!-- [updated] -->
Testing is non‑negotiable. Unit tests cover business logic; integration tests cover  <!-- [updated] -->
key flows (orders, services, users); UI smoke tests cover registration, login, and  <!-- [updated] -->
create‑order. Tests MUST be deterministic (mock time/network; isolated DB). Overall  <!-- [updated] -->
coverage MUST be ≥85% with agreed per‑package minima; CI is the source of truth.  <!-- [updated] -->

### UX Consistency and Accessibility  <!-- [updated] -->
UI MUST meet WCAG 2.1 AA for new work with no regressions. Shared components/partials  <!-- [updated] -->
for common UI (headers, forms, buttons) MUST be used. Pages MUST be keyboard  <!-- [updated] -->
navigable with visible focus, proper ARIA, and clear empty/loading/error states.  <!-- [updated] -->

### Performance and Efficiency  <!-- [updated] -->
Backend endpoints MUST meet SLOs: p95 <300ms for cached GETs, p95 <600ms for key  <!-- [updated] -->
uncached paths; p99 error rate <0.5%. Prevent N+1 via select_related/prefetch_related  <!-- [updated] -->
and maintain query budgets (detail ≤10, list ≤30). Cache expensive views; enforce  <!-- [updated] -->
page weight budgets (≤200KB gzipped CSS+JS) and lazy‑load images.  <!-- [updated] -->

### Security and Observability  <!-- [updated] -->
Production MUST run with DEBUG=False, proper ALLOWED_HOSTS, CSRF enabled, and secure  <!-- [updated] -->
cookies. Structured logging with request IDs and basic timings MUST be present;  <!-- [updated] -->
key failures and performance outliers SHOULD be visible via logs or dashboards.  <!-- [updated] -->

## Technology Stack and Environments  <!-- [updated] -->

- Framework: Django (Python 3.x).  <!-- [updated] -->
- Local database: sqlite3 (file at `YourPlanner/db.sqlite3`).  <!-- [updated] -->
- Staging/Production database: PostgreSQL.  <!-- [updated] -->
- Web: Nginx → Gunicorn (systemd) → Django apps.  <!-- [updated] -->
- Static files: collectstatic to `YourPlanner/staticfiles/`; served by Nginx.  <!-- [updated] -->
- Media: stored under `YourPlanner/media/` with appropriate protections.  <!-- [updated] -->
- Config/secrets: environment variables (never checked into VCS).  <!-- [updated] -->

## Development Workflow and Quality Gates  <!-- [updated] -->

- PR checklist MUST confirm: formatted, linted, imports sorted, types checked, tests  <!-- [updated] -->
	updated/passing, accessibility considered (screenshots for UI), and performance  <!-- [updated] -->
	impact evaluated (queries, caching, assets).  <!-- [updated] -->
- CI gates (merge‑blocking): black --check; ruff; isort --check‑only; mypy; pytest  <!-- [updated] -->
	with coverage ≥85%; Playwright smoke; Bandit and Gitleaks with zero high/critical.  <!-- [updated] -->
- Flaky tests MUST be quarantined and fixed within 7 days.  <!-- [updated] -->

## Governance  <!-- [updated] -->

- Amendments: Open a PR modifying this file with rationale, examples, and a migration  <!-- [updated] -->
	or rollout plan. Tag at least Backend, QA, and UX reviewers.  <!-- [updated] -->
- Approvals: All merge‑blocking CI gates MUST be green; require sign‑off from domain  <!-- [updated] -->
	reviewers (Backend, QA, UX) for relevant changes.  <!-- [updated] -->
- Versioning: Semantic—MAJOR for removals/incompatible changes; MINOR for new/expanded  <!-- [updated] -->
	sections or principles; PATCH for clarifications.  <!-- [updated] -->
- Compliance: Review at least quarterly; backlog tasks created for any gaps and tracked  <!-- [updated] -->
	to closure.  <!-- [updated] -->

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): unknown  | **Last Amended**: 2025-10-21  <!-- [updated] -->
