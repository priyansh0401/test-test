from rest_framework import serializers
from .models import Camera
from .validators import validate_camera_connection

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = [
            'id', 'name', 'ip_address', 'location', 'description', 
            'status', 'thumbnail', 'camera_type', 'enable_motion_detection', 
            'enable_sound_detection', 'stream_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'thumbnail', 'stream_url', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        
        # Validate camera connection
        ip_address = validated_data.get('ip_address')
        is_reachable, status = validate_camera_connection(ip_address)
        
        if not is_reachable:
            raise serializers.ValidationError({"ip_address": "Camera is unreachable. Please check the IP address."})
        
        # Set the status based on the connection check
        validated_data['status'] = status
        
        # Create the camera
        return super().create(validated_data)
