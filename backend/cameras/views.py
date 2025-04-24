from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Camera
from .serializers import CameraSerializer
from .validators import validate_camera_connection, capture_camera_thumbnail
import threading

class CameraViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Camera model
    """
    serializer_class = CameraSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all cameras
        for the currently authenticated user.
        """
        return Camera.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Save the camera and capture a thumbnail in the background
        """
        camera = serializer.save()
        
        # Capture thumbnail in a background thread
        threading.Thread(target=self._capture_thumbnail, args=(camera.id,)).start()
    
    def _capture_thumbnail(self, camera_id):
        """
        Helper method to capture a thumbnail for a camera
        """
        try:
            camera = Camera.objects.get(id=camera_id)
            capture_camera_thumbnail(camera)
        except Camera.DoesNotExist:
            pass
    
    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        """
        Check the status of a camera
        """
        camera = self.get_object()
        is_reachable, status = validate_camera_connection(camera.ip_address)
        
        # Update the camera status
        camera.status = status
        camera.save()
        
        # If the camera is online, capture a thumbnail
        if status == 'online':
            threading.Thread(target=self._capture_thumbnail, args=(camera.id,)).start()
        
        return Response({
            'id': camera.id,
            'name': camera.name,
            'status': camera.status,
            'is_reachable': is_reachable
        })
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """
        Test connection to a camera without creating it
        """
        ip_address = request.data.get('ip_address')
        camera_type = request.data.get('camera_type', 'ip')
        
        if not ip_address:
            return Response(
                {"error": "IP address is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Form the proper URL based on camera type
        url = ip_address
        if not url.startswith(('rtsp://', 'http://', 'https://')):
            if camera_type == 'rtsp':
                url = f"rtsp://{url}:554/stream"
            elif camera_type == 'onvif':
                url = f"rtsp://{url}:554/onvif1"
            elif camera_type == 'ip':
                url = f"http://{url}"
        
        is_reachable, status_value = validate_camera_connection(url)
        
        return Response({
            'ip_address': ip_address,
            'url': url,
            'is_reachable': is_reachable,
            'status': status_value
        })
