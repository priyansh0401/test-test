from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .serializers import AlertSerializer

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Alert model (read-only)
    """
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all alerts
        for the cameras owned by the currently authenticated user.
        """
        return Alert.objects.filter(camera__user=self.request.user)
