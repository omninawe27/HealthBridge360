from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create superuser if it does not exist'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING('Superuser environment variables not set. Skipping superuser creation.')
            )
            return

        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            # Update existing superuser with new credentials
            superuser.username = username
            superuser.email = email
            superuser.set_password(password)
            superuser.phone_number = '+1234567891'
            superuser.first_name = 'Super'
            superuser.last_name = 'Admin'
            superuser.save()
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" updated successfully.')
            )
        else:
            # Create new superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                phone_number='+1234567891',  # Add required phone_number field (different from existing)
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully.')
            )
