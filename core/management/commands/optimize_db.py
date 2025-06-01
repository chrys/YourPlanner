from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Performs database optimization tasks like analyzing tables and updating statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Run ANALYZE on tables to update statistics',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM to reclaim storage and update statistics',
        )
        parser.add_argument(
            '--reindex',
            action='store_true',
            help='Rebuild indexes to improve query performance',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization tasks',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Specify a model to optimize (format: app_label.model_name)',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        # Get the list of models to optimize
        if options['model']:
            try:
                app_label, model_name = options['model'].split('.')
                models = [apps.get_model(app_label, model_name)]
                self.stdout.write(f"Optimizing single model: {options['model']}")
            except (ValueError, LookupError) as e:
                self.stderr.write(f"Error: {e}")
                self.stderr.write("Format should be 'app_label.model_name'")
                return
        else:
            models = apps.get_models()
            self.stdout.write("Optimizing all models")
        
        # Determine which operations to run
        run_all = options['all']
        run_analyze = options['analyze'] or run_all
        run_vacuum = options['vacuum'] or run_all
        run_reindex = options['reindex'] or run_all
        
        if not any([run_analyze, run_vacuum, run_reindex]):
            self.stdout.write("No optimization tasks specified. Use --analyze, --vacuum, --reindex, or --all")
            return
        
        # Execute the optimization tasks
        with connection.cursor() as cursor:
            for model in models:
                table_name = model._meta.db_table
                self.stdout.write(f"Processing table: {table_name}")
                
                try:
                    if run_analyze:
                        self.stdout.write(f"  Analyzing {table_name}...")
                        cursor.execute(f"ANALYZE {table_name}")
                    
                    if run_vacuum:
                        self.stdout.write(f"  Vacuuming {table_name}...")
                        # Note: VACUUM cannot run inside a transaction block in PostgreSQL
                        # For SQLite, this is fine
                        cursor.execute(f"VACUUM {table_name}")
                    
                    if run_reindex:
                        self.stdout.write(f"  Reindexing {table_name}...")
                        cursor.execute(f"REINDEX TABLE {table_name}")
                        
                except Exception as e:
                    self.stderr.write(f"Error optimizing {table_name}: {e}")
                    logger.error(f"Database optimization error: {e}", exc_info=True)
        
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"Database optimization completed in {elapsed_time:.2f} seconds"))

