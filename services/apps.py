from django.apps import AppConfig

#Django uses this class automatically when loading the app, as long as your INSTALLED_APPS entry 
# is 'services' (not 'services.apps.ServicesConfig').
class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
