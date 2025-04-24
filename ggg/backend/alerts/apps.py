from django.apps import AppConfig

class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts'
    
    def ready(self):
        # Import the alert simulator when the app is ready
        from . import simulator
        simulator.start()
