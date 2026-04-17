# CJ Web Studio — Django Backend

> Professional agency backend: quote pipeline, email notifications, EFT invoice tracking.  
> John Buhendwa · Durban, South Africa 🇿🇦

---

## What Was Fixed in This Version

| Bug | Fix |
|-----|-----|
| Form blinks, doesn't save | The static `contact.html` was POST-ing to itself. Django template uses `{% url 'quote_request' %}` — always hits Django correctly. |
| No emails received | `django-environ` was imported but not installed — Django crashed on startup. Removed it, used plain `os.environ` instead. |
| `{{ agency.name }}` empty in templates | No context processor was passing AGENCY to base.html. Added `quotes/context_processors.py` and registered it. |
| Charts fall on scroll | Chart.js default re-animates on scroll. Fixed with `animation: false` in all charts. |
| Emails look AI-generated | Rewrote both email templates to sound personal and human. |
| Admin crash on load | `list_editable` and `list_display_links` had overlapping fields. Fixed. |

---

## Project Structure

```
cj_backend_v2/
├── manage.py
├── requirements.txt
├── .env.example                   ← Copy to .env in production
│
├── cj_studio/
│   ├── settings.py                ← All config: email, DB, AGENCY info
│   ├── urls.py                    ← Root URL routing
│   └── wsgi.py
│
├── quotes/
│   ├── models.py                  ← QuoteRequest, Project, Invoice, Payment
│   ├── forms.py                   ← Validated quote form
│   ├── views.py                   ← quote_request, quote_success, invoice_view
│   ├── admin.py                   ← Full CRM admin panel
│   ├── emails.py                  ← Email sending (admin alert + client reply)
│   ├── urls.py                    ← App URL patterns
│   ├── context_processors.py      ← Injects AGENCY into all templates
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── management/commands/
│   │   └── setup_agency.py        ← One-command setup
│   └── templates/quotes/
│       ├── contact.html           ← Client quote form
│       ├── success.html           ← Post-submission confirmation
│       └── invoice.html           ← Printable invoice page
│
├── templates/
│   ├── base.html                  ← Shared layout (dark navy, CJ Web Studio style)
│   ├── admin/
│   │   ├── base_site.html         ← Custom admin branding
│   │   └── index.html             ← Dashboard with charts (Chart.js)
│   └── emails/
│       ├── admin_notification.html    ← Email to John on new lead
│       ├── client_confirmation.html   ← Auto-reply to client
│       └── invoice_notification.html  ← Invoice email to client
│
└── static/
    ├── css/
    │   ├── tokens.css             ← Design variables (same as frontend)
    │   ├── base.css               ← Global styles
    │   └── layout.css             ← Page layouts
    ├── js/
    │   ├── main.js
    │   └── animations.js
    └── images/
        └── logo.jpg
```

---

## Quick Start

### Step 1 — Prerequisites

```bash
python --version   # Must be Python 3.10+
```

### Step 2 — Install dependencies

```bash
cd cj_backend_v2
pip install -r requirements.txt
```

### Step 3 — Set up the database

```bash
python manage.py migrate
```

### Step 4 — Create admin account + sample data

```bash
python manage.py setup_agency
```

This creates:
- **Username:** `john`
- **Password:** `maestrojdd`
- One sample quote so the admin isn't empty

### Step 5 — Start the server

```bash
python manage.py runserver
```

### Step 6 — Open in browser

| URL | What it is |
|-----|-----------|
| `http://127.0.0.1:8000/` | Client quote form |
| `http://127.0.0.1:8000/success/` | Confirmation page |
| `http://127.0.0.1:8000/admin/` | Admin panel (john / maestrojdd) |
| `http://127.0.0.1:8000/invoice/<number>/?token=<token>` | Client invoice page |

---

## Connecting Your Frontend

**The most common mistake:** The static `contact.html` in your frontend website points to `action="http://127.0.0.1:8000/"` — this only works when Django is running locally. When deployed, update it to your domain:

```html
<!-- In your static contact.html -->
<form method="POST" action="https://your-backend.railway.app/">
  <!-- Add CSRF token handling (see CSRF section below) -->
</form>
```

**Simpler option:** Replace your static `contact.html` with Django's template (`quotes/templates/quotes/contact.html`). It handles everything automatically.

---

## Email Setup

### Development (default — prints to terminal)

Emails print to your terminal window. You'll see the full email content there. No Gmail needed.

```python
# settings.py — already set
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (real Gmail)

**Get a Gmail App Password first:**
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Turn on 2-Step Verification if not already on
3. Go to **Security → App Passwords**
4. Create: Mail → Other → name it "Django CJ Studio"
5. Copy the 16-character password

**Then update `settings.py`:**

```python
# Comment out:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Uncomment and fill in:
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'cibangukaj@gmail.com'
EMAIL_HOST_PASSWORD = 'paste-your-16-char-app-password-here'
DEFAULT_FROM_EMAIL  = 'CJ Web Studio <cibangukaj@gmail.com>'
```

---

## How the Pipeline Works

Every form submission creates a `QuoteRequest` in the database with status `New`.

Move leads through the pipeline from `/admin/quotes/quoterequest/`:

| Status | When to use |
|--------|-------------|
| **New** | Just submitted — haven't replied yet |
| **Contacted** | You've replied to the client |
| **Briefed** | You've sent the project brief |
| **In Progress** | 50% deposit received, build started |
| **Revision** | Client requested changes |
| **Completed** | Live, final payment received |
| **Cancelled** | Didn't proceed |

**Bulk actions** — tick multiple quotes, use the Action dropdown to move them all at once.

---

## EFT Invoice Tracking

Since payment is EFT (no payment gateway), you record payments manually.

1. Open a `QuoteRequest` → click "Save and continue editing"
2. At the top, click **Projects** → **Add Project** to create the project record
3. Inside the Project, go to the **Invoices** inline section
4. Add a **Deposit Invoice** (50% of agreed price)
5. Set EFT reference — tell the client to use this as their payment reference
6. When EFT appears in your bank: set status to **Paid**, fill in **Date Paid**
7. After project delivery: add **Final Balance Invoice**

**Invoice numbering:** Auto-generated as `CJ-INV-0001`, `CJ-INV-0002`, etc.

---

## Adding Your Bank Details

Open `settings.py` and fill in the `AGENCY['bank']` section:

```python
AGENCY = {
    ...
    'bank': {
        'name':        'First National Bank',
        'account':     '62XXXXXXXXX',     # Your account number
        'branch_code': '250655',           # FNB universal branch code
    },
}
```

This auto-populates the EFT details on every invoice.

---

## Deployment (Railway — Free)

1. Push your project to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add these environment variables in Railway dashboard:

```
DJANGO_SECRET_KEY    = (generate at djecrety.ir)
DJANGO_DEBUG         = False
DJANGO_ALLOWED_HOSTS = your-app.railway.app
EMAIL_HOST_USER      = cibangukaj@gmail.com
EMAIL_HOST_PASSWORD  = your-16-char-app-password
```

4. Add this to `settings.py` for production:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

5. Railway gives you a public URL. Update `AGENCY['website']` in settings.py to match.

---

## Troubleshooting

**"Module not found: django"**  
→ Virtual environment not active. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

**"Table doesn't exist"**  
→ Run `python manage.py migrate`

**Form submits but nothing saves / page blinks**  
→ The form's `action` URL isn't pointing to Django. Use the Django template (`contact.html`) not the static HTML file directly.

**Emails not arriving in production**  
→ Must be a Gmail App Password (16 chars), NOT your regular password. Go to myaccount.google.com/security → App Passwords.

**Admin page looks unstyled**  
→ Run `python manage.py collectstatic` then refresh.

**Charts animate/fall on scroll**  
→ Already fixed in this version (`animation: false` in all charts).

---

## Models at a Glance

```
QuoteRequest          ← One per form submission
    └── Project       ← Created when quote is accepted (1-to-1)
            └── Invoice   ← One per invoice (deposit/final/retainer)
                    └── Payment   ← One per EFT payment received
```

---

*CJ Web Studio Backend v2 — all bugs fixed, ready to deploy.*
