from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('reference', models.CharField(editable=False, max_length=12, unique=True)),
                ('name', models.CharField(max_length=120, verbose_name='Full Name')),
                ('email', models.EmailField(verbose_name='Email Address')),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('business_name', models.CharField(blank=True, max_length=120)),
                ('project_type', models.CharField(
                    choices=[('landing_page','Landing Page'),('business_site','Business Website (5+ pages)'),
                             ('web_app','Web App / Portal'),('ecommerce','E-Commerce Store'),
                             ('three_d','3D / Interactive'),('cad','CAD / Architectural Drawing'),('other','Other')],
                    default='other', max_length=30)),
                ('budget', models.CharField(
                    blank=True,
                    choices=[('r2500_5000','R2,500 - R5,000'),('r5000_12000','R5,000 - R12,000'),
                             ('r12000_25000','R12,000 - R25,000'),('r25000_plus','R25,000+')],
                    max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(
                    choices=[('new','New'),('contacted','Contacted'),('briefed','Briefed'),
                             ('in_progress','In Progress'),('revision','Revision'),
                             ('completed','Completed'),('cancelled','Cancelled')],
                    db_index=True, default='new', max_length=20)),
                ('internal_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin_notified', models.BooleanField(default=False)),
                ('client_notified', models.BooleanField(default=False)),
            ],
            options={'verbose_name':'Quote Request','verbose_name_plural':'Quote Requests','ordering':['-created_at']},
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('agreed_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_structure', models.CharField(
                    choices=[('deposit_50','50% Deposit + 50% on Completion'),('full','Full Payment Upfront'),
                             ('monthly','Monthly Retainer'),('milestone','Milestone-based')],
                    default='deposit_50', max_length=20)),
                ('payment_status', models.CharField(
                    choices=[('pending','Pending'),('partial','Deposit Paid'),('paid','Fully Paid'),
                             ('overdue','Overdue'),('refunded','Refunded')],
                    default='pending', max_length=20)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('delivery_url', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quote', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='project', to='quotes.quoterequest')),
            ],
            options={'verbose_name':'Project','verbose_name_plural':'Projects','ordering':['-created_at']},
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('invoice_number', models.CharField(editable=False, max_length=20, unique=True)),
                ('invoice_type', models.CharField(
                    choices=[('deposit','Deposit Invoice (50%)'),('final','Final Balance Invoice'),
                             ('full','Full Payment Invoice'),('retainer','Monthly Retainer Invoice')],
                    default='deposit', max_length=12)),
                ('status', models.CharField(
                    choices=[('draft','Draft'),('sent','Sent'),('paid','Paid'),('overdue','Overdue'),('void','Void')],
                    default='draft', max_length=12)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('vat_rate', models.DecimalField(decimal_places=2, default=15.0, max_digits=5)),
                ('issued_date', models.DateField(default=django.utils.timezone.now)),
                ('due_date', models.DateField()),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoices', to='quotes.project')),
            ],
            options={'verbose_name':'Invoice','verbose_name_plural':'Invoices','ordering':['-issued_date']},
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(
                    choices=[('eft','EFT / Bank Transfer'),('cash','Cash'),('other','Other')],
                    default='eft', max_length=15)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('received_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='quotes.invoice')),
            ],
            options={'verbose_name':'Payment','verbose_name_plural':'Payments','ordering':['-received_at']},
        ),
    ]
