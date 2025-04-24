from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from cameras.models import Camera
from .models import Alert
from channels.testing import WebsocketCommunicator
from guardian_eye.asgi import application
import json

User = get_user_model()

class AlertTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        # Get JWT token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        }, format='json')
        
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create a camera
        self.camera = Camera.objects.create(
            user=self.user,
            name='Test Camera',
            ip_address='192.168.1.100',
            location='Test Location',
            status='online'
        )
        
        # Create some alerts
        Alert.objects.create(
            camera=self.camera,
            alert_type='Motion',
            message='Motion detected at Test Location'
        )
        Alert.objects.create(
            camera=self.camera,
            alert_type='Crying',
            message='Crying sound detected at Test Location'
        )
        
    def test_list_alerts(self):
        """Test listing alerts"""
        url = reverse('alert-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        communicator = WebsocketCommunicator(
            application,
            f'/ws/alerts/{self.user.id}/'
        )
        connected, _ = await communicator.connect()
        
        self.assertTrue(connected)
        
        # Disconnect
        await communicator.disconnect()
        
    async def test_websocket_alert(self):
        """Test receiving alert via WebSocket"""
        communicator = WebsocketCommunicator(
            application,
            f'/ws/alerts/{self.user.id}/'
        )
        connected, _ = await communicator.connect()
        
        self.assertTrue(connected)
        
        # Simulate sending an alert
        from alerts.simulator import send_alert_to_websocket
        alert_data = {
            'id': 3,
            'camera_id': self.camera.id,
            'camera_name': self.camera.name,
            'alert_type': 'Motion',
            'message': 'Test alert',
            'timestamp': '2023-01-01T00:00:00Z'
        }
        send_alert_to_websocket(alert_data)
        
        # Receive the alert
        response = await communicator.receive_json_from()
        
        self.assertEqual(response['camera_name'], self.camera.name)
        self.assertEqual(response['alert_type'], 'Motion')
        self.assertEqual(response['message'], 'Test alert')
        
        # Disconnect
        await communicator.disconnect()
