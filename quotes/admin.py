"""
quotes/admin.py — CJ Web Studio
Fixed issues:
- list_editable conflicting with list_display_links (caused admin crash)
- Dashboard stats now passed via overridden index view
- Chart data correctly serialised as JSON
"""

import json
from datetime            import date, timedelta

from django.contrib      import admin
from django.utils.html   import format_html
from django.db.models    import Count
from django.utils        import timezone

from .models             import QuoteRequest, Project, Invoice, Payment
from .emails             import send_admin_notification, send_client_confirmation, send_invoice_email


# ─── ADMIN SITE LABELS ───────────────────────────────────────────────────────
admin.site.site_header  = 'CJ Web Studio'
admin.site.site_title   = 'CJ Web Studio Admin'
admin.site.index_title  = 'Client Pipeline Dashboard'


# ─── DASHBOARD DATA ───────────────────────────────────────────────────────────
def _dashboard_data():
    """Build chart and stats data for the admin index page."""
    six_months_ago = date.today() - timedelta(days=180)
    qs = QuoteRequest.objects.all()

    # Stats
    stats = {
        'total_quotes':     qs.count(),
        'new_quotes':       qs.filter(status='new').count(),
        'contacted_quotes': qs.filter(status='contacted').count(),
        'in_progress_quotes': qs.filter(status='in_progress').count(),
        'completed_quotes': qs.filter(status='completed').count(),
        'recent_quotes':    qs[:10],
    }

    # Line chart — quotes per month over last 6 months
    monthly = qs.filter(created_at__date__gte=six_months_ago).dates('created_at', 'month', order='ASC')
    quote_labels = [dt.strftime('%b %Y') for dt in monthly]
    quote_counts = [
        qs.filter(created_at__year=dt.year, created_at__month=dt.month).count()
        for dt in monthly
    ]

    # Budget bar chart
    budget_choices = dict(QuoteRequest._meta.get_field('budget').choices)
    budget_data = (
        qs.exclude(budget='').values('budget')
          .annotate(n=Count('id')).order_by('-n')
    )
    budget_labels = [budget_choices.get(b['budget'], b['budget']) for b in budget_data]
    budget_counts = [b['n'] for b in budget_data]

    # Project type doughnut
    type_choices = dict(QuoteRequest._meta.get_field('project_type').choices)
    type_data = (
        qs.values('project_type').annotate(n=Count('id')).order_by('-n')
    )
    project_labels = [type_choices.get(t['project_type'], t['project_type']) for t in type_data]
    project_counts = [t['n'] for t in type_data]

    return {
        **stats,
        'quote_labels':   json.dumps(quote_labels),
        'quote_counts':   json.dumps(quote_counts),
        'budget_labels':  json.dumps(budget_labels),
        'budget_counts':  json.dumps(budget_counts),
        'project_labels': json.dumps(project_labels),
        'project_counts': json.dumps(project_counts),
    }


# Monkey-patch the admin index to inject our dashboard data
_orig_index = admin.site.__class__.index

def _custom_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update(_dashboard_data())
    return _orig_index(self, request, extra_context=extra_context)

admin.site.__class__.index = _custom_index


# ─── STATUS BADGE COLOURS ────────────────────────────────────────────────────
_STATUS_COLOUR = {
    'new':         '#3b82f6',
    'contacted':   '#f59e0b',
    'briefed':     '#06b6d4',
    'in_progress': '#8b5cf6',
    'revision':    '#ec4899',
    'completed':   '#10b981',
    'cancelled':   '#64748b',
}


# ─── QUOTE REQUEST ────────────────────────────────────────────────────────────
@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):

    # FIX: can't have list_editable AND the same field in list_display_links
    # Solution: put 'reference' as the clickable link, status editable inline
    list_display        = ['reference', 'name', 'email', 'phone', 'project_type_badge', 'budget_display', 'status_badge', 'created_at']
    list_display_links  = ['reference', 'name']   # These are clickable
    list_filter         = ['status', 'project_type', 'budget', 'created_at']
    search_fields       = ['name', 'email', 'phone', 'reference', 'business_name', 'message']
    ordering            = ['-created_at']
    date_hierarchy      = 'created_at'
    readonly_fields     = ['reference', 'created_at', 'updated_at', 'admin_notified', 'client_notified']

    fieldsets = [
        ('Client', {
            'fields': ('reference', 'name', 'email', 'phone', 'business_name')
        }),
        ('Project', {
            'fields': ('project_type', 'budget', 'message')
        }),
        ('Pipeline', {
            'fields': ('status', 'internal_notes')
        }),
        ('Notifications', {
            'fields': ('admin_notified', 'client_notified'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]

    actions = ['mark_contacted', 'mark_in_progress', 'mark_completed', 'resend_client_email']

    @admin.display(description='Project', ordering='project_type')
    def project_type_badge(self, obj):
        return format_html(
            '<span style="background:#1e2740;color:#94a3b8;padding:2px 8px;border-radius:6px;font-size:11px">{}</span>',
            obj.get_project_type_display()
        )

    @admin.display(description='Budget', ordering='budget')
    def budget_display(self, obj):
        return obj.get_budget_display() or '—'

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        colour = _STATUS_COLOUR.get(obj.status, '#64748b')
        return format_html(
            '<span style="background:{c};color:#fff;padding:3px 10px;border-radius:999px;'
            'font-size:11px;font-weight:700;letter-spacing:0.04em">{label}</span>',
            c=colour,
            label=obj.get_status_display()
        )

    @admin.action(description='Mark selected → Contacted')
    def mark_contacted(self, request, queryset):
        n = queryset.update(status='contacted')
        self.message_user(request, f'{n} quote(s) marked as Contacted.')

    @admin.action(description='Mark selected → In Progress')
    def mark_in_progress(self, request, queryset):
        n = queryset.update(status='in_progress')
        self.message_user(request, f'{n} quote(s) marked as In Progress.')

    @admin.action(description='Mark selected → Completed')
    def mark_completed(self, request, queryset):
        n = queryset.update(status='completed')
        self.message_user(request, f'{n} quote(s) marked as Completed.')

    @admin.action(description='Re-send auto-reply to client')
    def resend_client_email(self, request, queryset):
        sent = sum(1 for q in queryset if send_client_confirmation(q))
        self.message_user(request, f'Auto-reply sent to {sent} client(s).')


# ─── PAYMENT INLINE ──────────────────────────────────────────────────────────
class PaymentInline(admin.TabularInline):
    model  = Payment
    extra  = 1
    fields = ['amount', 'payment_method', 'reference', 'received_at', 'notes']


# ─── INVOICE ─────────────────────────────────────────────────────────────────
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display       = ['invoice_number', 'client_name', 'invoice_type', 'amount_fmt', 'vat_fmt', 'total_fmt', 'status_badge', 'due_date']
    list_display_links = ['invoice_number']
    list_filter        = ['status', 'invoice_type', 'issued_date']
    search_fields      = ['invoice_number', 'project__title', 'project__quote__name']
    ordering           = ['-issued_date']
    readonly_fields    = ['invoice_number', 'created_at']
    inlines            = [PaymentInline]
    actions            = ['send_to_client', 'mark_paid']

    @admin.display(description='Client', ordering='project__quote__name')
    def client_name(self, obj):
        return obj.project.quote.name

    @admin.display(description='Excl. VAT')
    def amount_fmt(self, obj):
        return f'R {obj.amount:,.2f}'

    @admin.display(description='VAT')
    def vat_fmt(self, obj):
        return f'R {obj.vat_amount:,.2f}'

    @admin.display(description='Total')
    def total_fmt(self, obj):
        return format_html('<strong>R {:,.2f}</strong>', obj.total_including_vat)

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        colours = {
            'draft': '#64748b', 'sent': '#3b82f6',
            'paid': '#10b981', 'overdue': '#ef4444', 'void': '#334155',
        }
        c = colours.get(obj.status, '#64748b')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            c, obj.get_status_display()
        )

    @admin.action(description='Email invoice to client')
    def send_to_client(self, request, queryset):
        sent = sum(1 for inv in queryset if send_invoice_email(inv))
        self.message_user(request, f'Invoice sent to {sent} client(s).')

    @admin.action(description='Mark selected as Paid')
    def mark_paid(self, request, queryset):
        n = queryset.update(status='paid', paid_date=timezone.now().date())
        self.message_user(request, f'{n} invoice(s) marked as Paid.')


# ─── PROJECT ─────────────────────────────────────────────────────────────────
class InvoiceInline(admin.TabularInline):
    model            = Invoice
    extra            = 0
    fields           = ['invoice_number', 'invoice_type', 'amount', 'status', 'due_date']
    readonly_fields  = ['invoice_number']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display       = ['title', 'client_name', 'agreed_price_fmt', 'paid_fmt', 'balance_fmt', 'payment_status_badge', 'start_date', 'deadline']
    list_display_links = ['title']
    list_filter        = ['payment_status', 'payment_structure', 'start_date']
    search_fields      = ['title', 'quote__name', 'quote__email']
    readonly_fields    = ['created_at', 'updated_at']
    inlines            = [InvoiceInline]

    @admin.display(description='Client', ordering='quote__name')
    def client_name(self, obj):
        return obj.quote.name

    @admin.display(description='Price')
    def agreed_price_fmt(self, obj):
        return f'R {obj.agreed_price:,.2f}'

    @admin.display(description='Paid')
    def paid_fmt(self, obj):
        return f'R {obj.amount_paid:,.2f}'

    @admin.display(description='Balance')
    def balance_fmt(self, obj):
        bal = obj.balance_due
        c = '#ef4444' if bal > 0 else '#10b981'
        return format_html('<span style="color:{};font-weight:700">R {:,.2f}</span>', c, bal)

    @admin.display(description='Payment', ordering='payment_status')
    def payment_status_badge(self, obj):
        c = {'pending':'#f59e0b','partial':'#3b82f6','paid':'#10b981','overdue':'#ef4444','refunded':'#8b5cf6'}.get(obj.payment_status,'#64748b')
        return format_html('<span style="color:{};font-weight:700">{}</span>', c, obj.get_payment_status_display())


# ─── PAYMENT ─────────────────────────────────────────────────────────────────
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display       = ['invoice', 'amount_fmt', 'payment_method', 'reference', 'received_at']
    list_display_links = ['invoice']
    list_filter        = ['payment_method', 'received_at']
    search_fields      = ['invoice__invoice_number', 'reference', 'invoice__project__quote__name']
    ordering           = ['-received_at']

    @admin.display(description='Amount')
    def amount_fmt(self, obj):
        return format_html('<strong>R {:,.2f}</strong>', obj.amount)
