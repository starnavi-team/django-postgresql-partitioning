from django.core.management.base import AppCommand

from ...utils import Partitioning


class Command(AppCommand):
    help = 'Setup partitioning'

    def handle_app_config(self, app_config, **options):
        models = app_config.get_models()
        partitionig_models = []

        for model in models:
            if hasattr(model, 'partitioning'):
                try:
                    Partitioning(model).setup()
                    partitionig_models.append(model.__name__)
                except ValueError as e:
                    self.stderr.write(str(e))

        self.stdout.write('Setup partitioning for model(s): {}'.format(
            ', '.join(partitionig_models)
        ))
