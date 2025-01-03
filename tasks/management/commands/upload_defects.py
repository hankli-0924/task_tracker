
import pandas as pd
from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
from django.conf import settings
class Command(BaseCommand):
    help = 'Upload CSV data to the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Load the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Create an SQLAlchemy engine using Django's database settings
        db_settings = settings.DATABASES['default']
        engine = create_engine(
            f"postgresql+psycopg2://{db_settings['USER']}:{db_settings['PASSWORD']}@"
            f"{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        )

        # Upload DataFrame to the database
        table_name = 'all_veriii_defects'  # 替换为实际表名
        with engine.begin() as connection:
            df.to_sql(name=table_name, con=connection, if_exists='append', index=False, chunksize=1000)

        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {csv_file} to {table_name}'))