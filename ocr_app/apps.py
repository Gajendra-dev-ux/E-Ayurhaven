from django.apps import AppConfig


class OcrAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ocr_app'

    def ready(self):
        import ocr_app.signals