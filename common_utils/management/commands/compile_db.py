import os

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    help = 'Compiles all database db code in specified or all applications.'

    def add_arguments(self, parser):
        parser.add_argument('--apps', '-a', nargs='+', type=str, default=None,
                            help='List of app names to compile db code for. If not provided, will compile for all apps.')

    def handle(self, *args, **options):
        app_names = options['apps'] or apps.get_app_configs()

        for app_config in app_names:
            if isinstance(app_config, str):  # If it's a string, get AppConfig instance
                try:
                    app_config = apps.get_app_config(app_config)
                except LookupError:
                    raise CommandError(f"App '{app_config}' does not exist.")

            # Assuming you have a standardized directory structure for SQL files
            sql_dir = os.path.join(app_config.path, 'db_code')
            # self.stdout.write(f'{sql_dir}')

            if os.path.exists(sql_dir):
                for file_name in sorted(os.listdir(sql_dir)):
                    if file_name.endswith('.sql'):
                        file_path = os.path.join(sql_dir, file_name)
                        self.stdout.write(self.style.SUCCESS(f'{file_path} execution starts.'))

                        with open(file_path, 'r') as f:
                            sql_content = f.read()

                        with connection.cursor() as cursor:
                            cursor.execute(sql_content)
                        self.stdout.write(self.style.SUCCESS(f'{file_path} have been compiled successfully.'))

        self.stdout.write(self.style.SUCCESS('All db code have been compiled successfully.'))
