# Dafara — architecture and delivery blueprint

## Scope for October 9

Django monolith with server-rendered templates, PostgreSQL in an isolated Docker Compose project, Gunicorn, and Nginx. SQLite is available for local rehearsal. No shared database credentials, repository, secrets, or volume with the Academy. Local-first development avoids burdening the existing t2.micro.

## Domains and relationships

| Domain | Current records | Next additions |
| --- | --- | --- |
| Identity | Django users, groups, explicit permissions | Staff assignments, MFA, donor accounts |
| Programs | Program, Case, Campaign | Projects, private Beneficiary, Verification |
| Funding | Demo Donation, Allocation | Provider Payment, webhook events, refunds, restricted funds |
| Delivery | Expense with private evidence reference | Receipt uploads, independent approvals, disbursements |
| Reporting | ImpactUpdate | Consent reviews, metrics definitions, published reports |
| Communications | Contact/volunteer Enquiry | Email queue, VolunteerProfile, delivery tracking |
| Accountability | Workflow AuditEvent | External append-only retention, security events |

Program has Cases. Each demonstration Case has one Campaign. A Campaign has Donations. Donations fund Allocations to that Case. Cases have Expenses, public-safe ImpactUpdates, and AuditEvents. Amounts use decimals. Allocation is capped at the requested amount; expense is capped at unspent allocated funding.

## Workflow

Submitted → Verified → Approved → In progress → Completed. Verification and approval require explicit permissions. Allocation starts delivery; completion requires the demo's full requested expense to be recorded. Publication is an explicit action after completion. Production will need partial-delivery closure and cancellation/reversal rules, plus independent verifier/approver checks.

## Information boundaries

| Audience | Visible information |
| --- | --- |
| Public | Published programs/campaigns, illustrative totals, approved anonymized outcomes |
| Field officer | Case details and private notes; verify permission |
| Program manager | Case details; approve, allocate, complete, publish permissions |
| Finance | Case details; record expense permission, view finance records where granted |
| Presentation manager | All workflow permissions for rehearsal; no automatic superuser status |
| Administrator | Setup and privileged administration; tightly controlled for real operations |

The MVP does not hold sensitive identities or uploads. Before storing real records, add object-level assigned-case access, purpose-based access to medical/survivor information, private object storage, expiring document links, consent policy, retention/deletion rules, and access logging. Roles are capabilities, not a hierarchy where everyone higher automatically sees everything.

## Donation integration after presentation

Use Dafara-owned provider credentials and hosted checkout. An authenticated signature-verified webhook, not a success-page visit, confirms payment. Store provider event IDs uniquely for idempotency, reconcile settlement/fees/refunds, and allocate only cleared or appropriately recognized funds. No live checkout is claimed in this package.

## Ownership

Dafara controls domain/DNS, organizational payment account, cloud account or explicit hosting agreement, source repository, recovery contacts, and backups. Technical access is delegated to the builder. Existing website content and images need preservation and owner verification; this demo uses proposed copy and no unverified impact statistics.

## Work through Friday

- Tuesday: runnable foundation and complete example workflow (this package).
- Wednesday: owner review of actual mission/programs, logo, approved content and payment-provider ownership; refine design.
- Thursday: target-host deployment and permissions checks, owner review of presentation, rehearse with a fresh demonstration case.
- Friday: present public experience, backstage delivery workflow, and the staged production roadmap.

## Before launch

Confirm operating policies and publication consent; back up and restore PostgreSQL; validate target Docker deployment; configure HTTPS, trusted proxy handling and MFA; add independent approvals and financial reconciliation; integrate verified payments and transactional email; load real data only after privacy/access controls are ready. Keep the demo isolated from the public organization site.
