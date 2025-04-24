from django.db import models
from django.conf import settings
from cameras.models import Camera

class Alert(models.Model):
    """
    Alert model to store alerts from cameras
    """
    ALERT_TYPES = (
        ('Motion', 'Motion'),
        ('Crying', 'Crying'),
    )
    
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.alert_type} alert from {self.camera.name} at {self.timestamp}"
