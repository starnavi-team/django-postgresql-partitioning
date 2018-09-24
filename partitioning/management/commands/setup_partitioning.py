from django.core.management.base import AppCommand

from ...utils import setup


class Command(AppCommand):
    help = 'Setup partitioning'

    def handle_app_config(self, app_config, **options):
        models = app_config.get_models()
        for model in models:
            if hasattr(model, 'partitioning'):
                setup(model)
