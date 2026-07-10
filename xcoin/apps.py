
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xcoin"

    def ready(self):
        import xcoin.signals