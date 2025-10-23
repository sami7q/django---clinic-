from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # من الأفضل ترك هذا السطر معلق مؤقتًا لتجنب ImportError
        # from . import signals
        pass
