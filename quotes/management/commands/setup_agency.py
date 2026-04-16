from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = 'Create superuser john/maestrojdd and seed a sample quote'

    def handle(self, *args, **options):
        if not User.objects.filter(username='john').exists():
            User.objects.create_superuser(username='john', email='cibangukaj@gmail.com', password='maestrojdd', first_name='John')
            self.stdout.write(self.style.SUCCESS('Superuser created: john / maestrojdd'))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'john' already exists."))
        from quotes.models import QuoteRequest
        if not QuoteRequest.objects.exists():
            QuoteRequest.objects.create(name='Sample Client', email='client@example.com', phone='+27 82 000 0000',
                business_name='Example Business', project_type='landing_page', budget='r5000_12000',
                message='Sample quote — delete this when ready.', status='new')
            self.stdout.write(self.style.SUCCESS('Sample quote created.'))
        self.stdout.write(self.style.SUCCESS('\nSetup done!\n  URL: http://127.0.0.1:8000/admin/\n  Username: john\n  Password: maestrojdd\n'))
