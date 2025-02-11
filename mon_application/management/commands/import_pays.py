import csv
from django.core.management.base import BaseCommand
from mon_application.models import Pays  

class Command(BaseCommand):
    help = "Import countries from a CSV file containing only country names"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help="Path to the CSV file containing country names"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if not row:  # Skip empty lines
                        continue
                    nom_pays = row[0].strip()  # Get the country name and remove extra spaces
                    Pays.objects.get_or_create(nom=nom_pays)
            self.stdout.write(self.style.SUCCESS("Successfully imported countries!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing countries: {e}"))
