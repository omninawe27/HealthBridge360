from django.core.management.base import BaseCommand
import os
import sys
import subprocess
import signal
import time

class Command(BaseCommand):
    help = 'Start the automated reminder service in the background'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon (background process)',
        )

    def handle(self, *args, **options):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

        if options['daemon']:
            # Start as daemon
            try:
                self.stdout.write('Starting reminder service as daemon...')

                process = subprocess.Popen([
                    sys.executable,
                    os.path.join(project_root, 'scripts', 'reminder_scheduler.py')
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_root)

                # Save PID
                with open(os.path.join(project_root, 'reminder_service.pid'), 'w') as f:
                    f.write(str(process.pid))

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Reminder service started with PID: {process.pid}'
                    )
                )
                self.stdout.write(
                    'Service is running in background. Check reminder_scheduler.log for logs.'
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to start service: {str(e)}')
                )
        else:
            # Interactive mode
            self.stdout.write('Starting reminder service (press Ctrl+C to stop)...')
            self.stdout.write('=' * 50)

            try:
                # Import and run the scheduler directly
                sys.path.insert(0, project_root)
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

                import django
                django.setup()

                from scripts.reminder_scheduler import main
                main()

            except KeyboardInterrupt:
                self.stdout.write('\nService stopped by user.')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Service error: {str(e)}')
                )
