import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import QuoteRequestForm
from .models import QuoteRequest, Invoice, Project
from .emails import send_admin_notification, send_client_confirmation

logger = logging.getLogger('quotes')


# ─── QUOTE REQUEST FORM ───────────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def quote_request(request):
    """
    GET  → Render the empty quote form.
    POST → Validate, save to DB, send emails, redirect to success page.
    If called via fetch() (AJAX), return JSON instead of redirect.
    """
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)

        if form.is_valid():
            # 1. Save to database
            quote = form.save()
            logger.info(f'New quote saved: {quote.reference} from {quote.email}')

            # 2. Send admin notification email
            try:
                send_admin_notification(quote)
                logger.info(f'Admin notification sent for {quote.reference}')
            except Exception as exc:
                logger.error(f'Admin email failed for {quote.reference}: {exc}')

            # 3. Send client auto-reply email
            try:
                send_client_confirmation(quote)
                logger.info(f'Client confirmation sent to {quote.email}')
            except Exception as exc:
                logger.error(f'Client email failed for {quote.reference}: {exc}')

            # 4. AJAX branch — return JSON if request came from fetch()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'message': f"Thanks! We've received your brief ({quote.reference}) and will reply within 24 hours.",
                    'reference': quote.reference,
                })

            # 5. Standard Django form submission — redirect to success page
            request.session['submitted_ref'] = quote.reference
            return redirect('quote_success')

        else:
            logger.warning(f'Form validation failed: {form.errors.as_json()}')

            # AJAX branch — return JSON errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: errs[0] for field, errs in form.errors.items()}
                return JsonResponse({
                    'status': 'error',
                    'error': 'Please check your details.',
                    'fields': errors
                }, status=400)

    else:
        form = QuoteRequestForm()

    return render(request, 'quotes/contact.html', {'form': form})


# ─── SUCCESS PAGE ─────────────────────────────────────────────────────────────
def quote_success(request):
    """
    Shown after a successful form submission.
    Reads the reference from the session (one-time, then clears it).
    If someone navigates here directly without submitting, redirect them.
    """
    reference = request.session.pop('submitted_ref', None)

    if not reference:
        return redirect('quote_request')

    return render(request, 'quotes/success.html', {
        'reference': reference,
    })


# ─── INVOICE VIEW ─────────────────────────────────────────────────────────────
def invoice_view(request, invoice_number):
    """
    Client-facing invoice page.
    Protected by a simple token — staff can always access it.
    """
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    token = request.GET.get('token', '')
    expected = _make_token(invoice)

    if token != expected and not request.user.is_staff:
        return HttpResponse('Access denied. Ask CJ Web Studio for the correct invoice link.', status=403)

    context = {
        'invoice': invoice,
        'project': invoice.project,
        'quote':   invoice.project.quote,
        'token':   expected,
    }

    # PDF download via ?pdf=1
    if request.GET.get('pdf') == '1':
        try:
            from weasyprint import HTML, CSS
            html_str = render_to_string('quotes/invoice.html', context, request=request)
            pdf = HTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf(
                stylesheets=[CSS(string='@page{size:A4;margin:18mm}')]
            )
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="CJ-Invoice-{invoice.invoice_number}.pdf"'
            return resp
        except ImportError:
            return HttpResponse(
                'PDF generation requires WeasyPrint. Run: pip install weasyprint',
                status=503
            )

    return render(request, 'quotes/invoice.html', context)


def _make_token(invoice):
    """Simple deterministic token for invoice URL sharing."""
    import hashlib
    raw = f'{invoice.invoice_number}{settings.SECRET_KEY[:12]}'
    return hashlib.sha256(raw.encode()).hexdigest()[:12]
