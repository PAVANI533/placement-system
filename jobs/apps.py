from django.apps import AppConfig

class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'

    def ready(self):
        # This ensures signals.py is loaded when Django starts
        import jobs.signals  # noqa