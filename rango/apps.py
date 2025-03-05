from django.apps import AppConfig

class UniSphereAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UniSphereApp'

class RangoConfig(AppConfig):
    name = 'rango'
