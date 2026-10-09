# Dafara presentation build

Working Django prototype for Friday, October 9, 2026. Updated to the approved teal-and-gold photo-led mockups: homepage, program detail with funding panel, and management sidebar/dashboard. Case search and stage filtering are functional. All three illustrative program photographs are bundled as local static assets. The monogram is a temporary code-rendered mark, pending Dafara’s real logo. Browser screenshot comparison is still required before claiming pixel-exact fidelity. Public website plus an authenticated case-to-impact demonstration. All seeded records are fictional. No live donations, tax receipts, emails, identity documents, or real beneficiary data.

## Start on your Mac

Requires Python 3.12 or newer. Extract the archive and open a terminal inside `dafara`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEBUG=1
export DEMO_MODE=1
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000. Sign in at `/login/` with the account you created. Staff management is `/management/`; Django administration is `/admin/`. No preset password is included. For a restricted presentation user, create a user in admin and assign the **Presentation manager** group. Superusers are only for setup.

## Eight-minute presentation

1. Open the homepage, Education program, and illustrative campaign.
2. Sign in and open `DEMO-EDU-001` in management.
3. Verify the case, then approve it.
4. Allocate the seeded $245 contribution.
5. Open Donate and record $65. Show the demo reference, not a real receipt.
6. Return to the case and allocate the additional funds: total $310.
7. Record a $310 expense, description `Tuition and learning materials`, evidence reference `DEMO-RECEIPT-001`.
8. Mark delivery complete, publish the anonymized outcome, and open Impact.
9. Show case history. Explain that public updates exclude private notes and evidence references.

To rehearse again, use a fresh local database or create a new case/campaign through admin. `seed_demo` is idempotent and does not reset a completed case.

## Separate EC2 demonstration stack

Keep this folder separate from KiraEdu: `/home/ubuntu/apps/dafara`. This package does not modify existing containers, DNS, or host Nginx. Its only published port is loopback `127.0.0.1:8091`. Confirm that port is unused before starting. The current 1 GiB EC2 remains capacity constrained; run locally first and assess headroom before adding containers.

```bash
cp .env.example .env
```

Edit `.env` locally. Generate unique random values for both secret fields (for example with `python3 -c 'import secrets; print(secrets.token_urlsafe(48))'`). Do not use example values. Keep `.env` private. Then:

```bash
docker compose build
docker compose up -d db
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py seed_demo
docker compose run --rm web python manage.py collectstatic --noinput
docker compose run --rm web python manage.py createsuperuser
docker compose up -d
```

From your own computer, tunnel the loopback port using your normal AWS SSH identity:

```bash
ssh -L 8091:127.0.0.1:8091 ubuntu@YOUR_EXISTING_SERVER
```

Open http://127.0.0.1:8091. No public inbound rule for 8091 is needed. Do not switch dafara.org for the presentation. The owner's existing site can remain online while this proposal is reviewed.

Before a public HTTPS deployment, configure a dedicated virtual host and certificate, update hosts/CSRF origins, set `COOKIE_SECURE=1`, review proxy trust and redirect handling, and add edge access restrictions for this demo. Do not enable SSL redirects behind a proxy until secure request detection is correctly configured. Nginx configuration here deliberately ignores client-supplied forwarded scheme headers. Limit request rules are only a basic safeguard, especially behind a proxy where clients may share a source IP.

## Verification

```bash
DEBUG=1 python manage.py check
DEBUG=1 python manage.py test
```

Automated tests cover the complete funding/delivery workflow, duplicate allocation protection, over-spend rejection, role authorization, public/private page boundaries, donation validation, live-mode payment blocking, and CSRF. Browser-based visual QA could not run because Chromium was unavailable and its download failed. Mobile responsiveness is implemented in CSS but still needs an actual device check. SQLite is tested locally; PostgreSQL/Docker must be verified on the target host before presentation deployment.

## Current limits

This is a presentation prototype, not a launched NGO financial system. The administration UI provides program/case/campaign creation; polished custom creation forms are a later step. Expense evidence is a private reference, not an uploaded receipt. Donors have no authenticated history portal yet. There is no payment-provider webhook, refund handling, currency conversion, email delivery, beneficiary identity store, or volunteer assignment workflow. Contact/volunteer forms save demonstration enquiries only. Amounts are illustrative USD.

Audit history is append-only through the workflow and read-only in Django admin; database administrators can still alter records. No claim of immutable or tamper-evident storage is made. Built-in superusers can bypass all role restrictions. Published impact copy needs an owner-controlled review process before real use. The demo workflow permits one authorized presentation manager to perform all steps; independent financial approvals and staff assignment boundaries must be added before production.

AWS references: [security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html), [EC2 IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html).
