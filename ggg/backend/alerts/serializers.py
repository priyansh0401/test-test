from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'camera', 'camera_name', 'alert_type', 'message', 'timestamp']
        read_only_fields = ['id', 'timestamp']
