"""
quotes/models.py — CJ Web Studio
Full pipeline: QuoteRequest → Project → Invoice → Payment
"""

from django.db   import models
from django.utils import timezone


class QuoteRequest(models.Model):

    class Status(models.TextChoices):
        NEW         = 'new',         'New'
        CONTACTED   = 'contacted',   'Contacted'
        BRIEFED     = 'briefed',     'Briefed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVISION    = 'revision',    'Revision'
        COMPLETED   = 'completed',   'Completed'
        CANCELLED   = 'cancelled',   'Cancelled'

    class ProjectType(models.TextChoices):
        LANDING_PAGE  = 'landing_page',  'Landing Page'
        BUSINESS_SITE = 'business_site', 'Business Website (5+ pages)'
        WEB_APP       = 'web_app',       'Web App / Portal'
        ECOMMERCE     = 'ecommerce',     'E-Commerce Store'
        THREE_D       = 'three_d',       '3D / Interactive'
        CAD           = 'cad',           'CAD / Architectural Drawing'
        OTHER         = 'other',         'Other'

    class BudgetRange(models.TextChoices):
        TIER_1 = 'r2500_5000',   'R2,500 – R5,000'
        TIER_2 = 'r5000_12000',  'R5,000 – R12,000'
        TIER_3 = 'r12000_25000', 'R12,000 – R25,000'
        TIER_4 = 'r25000_plus',  'R25,000+'

    # Auto-generated reference e.g. CJ-00001
    reference     = models.CharField(max_length=12, unique=True, editable=False)

    # Client info
    name          = models.CharField(max_length=120, verbose_name='Full Name')
    email         = models.EmailField(verbose_name='Email Address')
    phone         = models.CharField(max_length=30, blank=True, verbose_name='Phone / WhatsApp')
    business_name = models.CharField(max_length=120, blank=True, verbose_name='Business / Company')

    # Project brief
    project_type  = models.CharField(max_length=30, choices=ProjectType.choices, default=ProjectType.OTHER, verbose_name='Project Type')
    budget        = models.CharField(max_length=20, choices=BudgetRange.choices, blank=True, verbose_name='Budget Range')
    message       = models.TextField(verbose_name='Project Details / Message')

    # Pipeline
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True, verbose_name='Pipeline Status')
    internal_notes = models.TextField(blank=True, help_text='Private — NOT shown to client')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Enquiry Date')
    updated_at = models.DateTimeField(auto_now=True)

    # Email tracking
    admin_notified  = models.BooleanField(default=False, verbose_name='Admin notified?')
    client_notified = models.BooleanField(default=False, verbose_name='Auto-reply sent?')

    class Meta:
        verbose_name        = 'Quote Request'
        verbose_name_plural = 'Quote Requests'
        ordering            = ['-created_at']

    def __str__(self):
        return f'[{self.reference}] {self.name} — {self.get_project_type_display()}'

    def save(self, *args, **kwargs):
        if not self.reference:
            last = QuoteRequest.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.reference = f'CJ-{next_id:05d}'
        super().save(*args, **kwargs)

    @property
    def is_new(self):
        return self.status == self.Status.NEW


class Project(models.Model):

    class PaymentStructure(models.TextChoices):
        DEPOSIT_50   = 'deposit_50', '50% Deposit + 50% on Completion'
        FULL_UPFRONT = 'full',       'Full Payment Upfront'
        MONTHLY      = 'monthly',    'Monthly Retainer'
        MILESTONE    = 'milestone',  'Milestone-based'

    class PaymentStatus(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        PARTIAL  = 'partial',  'Deposit Paid'
        PAID     = 'paid',     'Fully Paid'
        OVERDUE  = 'overdue',  'Overdue'
        REFUNDED = 'refunded', 'Refunded'

    quote             = models.OneToOneField(QuoteRequest, on_delete=models.PROTECT, related_name='project')
    title             = models.CharField(max_length=200, verbose_name='Project Title')
    agreed_price      = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Agreed Price (ZAR)')
    payment_structure = models.CharField(max_length=20, choices=PaymentStructure.choices, default=PaymentStructure.DEPOSIT_50)
    payment_status    = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount_paid       = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Amount Paid (ZAR)')
    start_date        = models.DateField(null=True, blank=True)
    deadline          = models.DateField(null=True, blank=True)
    delivery_url      = models.URLField(blank=True, verbose_name='Live URL / Staging Link')
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Project'
        verbose_name_plural = 'Projects'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.quote.name}'

    @property
    def balance_due(self):
        return self.agreed_price - self.amount_paid

    @property
    def deposit_amount(self):
        return (self.agreed_price * 50) / 100


class Invoice(models.Model):

    class InvoiceType(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit Invoice (50%)'
        FINAL   = 'final',   'Final Balance Invoice'
        FULL    = 'full',    'Full Payment Invoice'
        RETAINER= 'retainer','Monthly Retainer Invoice'

    class InvoiceStatus(models.TextChoices):
        DRAFT   = 'draft',   'Draft'
        SENT    = 'sent',    'Sent'
        PAID    = 'paid',    'Paid'
        OVERDUE = 'overdue', 'Overdue'
        VOID    = 'void',    'Void'

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    project        = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='invoices')
    invoice_type   = models.CharField(max_length=12, choices=InvoiceType.choices, default=InvoiceType.DEPOSIT)
    status         = models.CharField(max_length=12, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate       = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    issued_date    = models.DateField(default=timezone.now)
    due_date       = models.DateField()
    paid_date      = models.DateField(null=True, blank=True)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering            = ['-issued_date']

    def __str__(self):
        return f'{self.invoice_number} | {self.project.quote.name} | R{self.amount}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.invoice_number = f'CJ-INV-{next_id:04d}'
        super().save(*args, **kwargs)

    @property
    def vat_amount(self):
        return (self.amount * self.vat_rate) / 100

    @property
    def total_including_vat(self):
        return self.amount + self.vat_amount


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        EFT   = 'eft',   'EFT / Bank Transfer'
        CASH  = 'cash',  'Cash'
        OTHER = 'other', 'Other'

    invoice        = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices, default=PaymentMethod.EFT)
    reference      = models.CharField(max_length=100, blank=True, help_text='Bank ref / transaction ID')
    received_at    = models.DateTimeField(default=timezone.now)
    notes          = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Payment'
        verbose_name_plural = 'Payments'
        ordering            = ['-received_at']

    def __str__(self):
        return f'R{self.amount} — {self.invoice.invoice_number}'
