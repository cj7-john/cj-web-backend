"""
quotes/emails.py — CJ Web Studio
All email sending logic. Fixed: no circular imports, proper error handling.
"""

import logging
from django.core.mail       import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html      import strip_tags
from django.conf            import settings

logger = logging.getLogger('quotes')
AGENCY = settings.AGENCY


def _send_email(subject, html_body, to_list, cc_list=None):
    """Core send helper. Returns True on success, False on failure."""
    text_body = strip_tags(html_body)
    msg = EmailMultiAlternatives(
        subject    = subject,
        body       = text_body,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = to_list,
        cc         = cc_list or [],
    )
    msg.attach_alternative(html_body, 'text/html')
    try:
        msg.send(fail_silently=False)
        logger.info(f'Email sent to {to_list}')
        return True
    except Exception as exc:
        logger.error(f'Email FAILED to {to_list}: {exc}')
        return False


def send_admin_notification(quote):
    """Notify John when a new quote comes in."""
    subject = f'New enquiry [{quote.reference}] — {quote.get_project_type_display()} · {quote.name}'
    html = render_to_string('emails/admin_notification.html', {'quote': quote, 'agency': AGENCY})
    sent = _send_email(subject, html, to_list=[settings.ADMIN_EMAIL])
    if sent:
        type(quote).objects.filter(pk=quote.pk).update(admin_notified=True)
    return sent


def send_client_confirmation(quote):
    """Auto-reply to the client immediately after submission."""
    first_name = quote.name.split()[0] if quote.name else quote.name
    subject = f'Got your brief, {first_name} — CJ Web Studio'
    html = render_to_string('emails/client_confirmation.html', {'quote': quote, 'agency': AGENCY})
    sent = _send_email(subject, html, to_list=[quote.email], cc_list=[settings.ADMIN_EMAIL])
    if sent:
        type(quote).objects.filter(pk=quote.pk).update(client_notified=True)
    return sent


def send_invoice_email(invoice):
    """Email an invoice to the client."""
    import hashlib
    token = hashlib.sha256(f'{invoice.invoice_number}{settings.SECRET_KEY[:12]}'.encode()).hexdigest()[:12]
    quote   = invoice.project.quote
    subject = f'Invoice {invoice.invoice_number} — {invoice.get_invoice_type_display()} · CJ Web Studio'
    html = render_to_string('emails/invoice_notification.html', {
        'invoice': invoice, 'project': invoice.project,
        'quote': quote, 'agency': AGENCY, 'token': token,
    })
    return _send_email(subject, html, to_list=[quote.email])
