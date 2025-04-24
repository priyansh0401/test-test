from django.db import models
from django.conf import settings
import uuid
import os

def camera_thumbnail_path(instance, filename):
    """Generate a unique path for camera thumbnails"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('camera_thumbnails', filename)

class Camera(models.Model):
    """
    Camera model to store camera information
    """
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )
    
    CAMERA_TYPE_CHOICES = (
        ('ip', 'IP Camera'),
        ('rtsp', 'RTSP Stream'),
        ('onvif', 'ONVIF Camera'),
        ('webcam', 'USB Webcam'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    thumbnail = models.ImageField(upload_to=camera_thumbnail_path, blank=True, null=True)
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPE_CHOICES, default='ip')
    enable_motion_detection = models.BooleanField(default=True)
    enable_sound_detection = models.BooleanField(default=False)
    stream_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    def save(self, *args, **kwargs):
        # Generate stream URL if not provided
        if not self.stream_url:
            if self.camera_type == 'rtsp':
                self.stream_url = self.ip_address
            elif self.camera_type == 'ip':
                # Default RTSP URL format for common IP cameras
                if not self.ip_address.startswith(('rtsp://', 'http://', 'https://')):
                    self.stream_url = f"rtsp://{self.ip_address}:554/stream"
                else:
                    self.stream_url = self.ip_address
            elif self.camera_type == 'onvif':
                # Default ONVIF URL format
                if not self.ip_address.startswith(('rtsp://', 'http://', 'https://')):
                    self.stream_url = f"rtsp://{self.ip_address}:554/onvif1"
                else:
                    self.stream_url = self.ip_address
        
        super().save(*args, **kwargs)
