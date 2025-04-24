from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Camera
from unittest.mock import patch

User = get_user_model()

class CameraTests(TestCase):
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
        
        self.camera_data = {
            'name': 'Test Camera',
            'ip_address': '192.168.1.100',
            'location': 'Test Location',
            'description': 'Test Description'
        }
        
    @patch('cameras.validators.validate_camera_connection')
    def test_add_camera(self, mock_validate):
        """Test adding a camera"""
        # Mock the camera validation to return True
        mock_validate.return_value = (True, 'online')
        
        url = reverse('camera-list')
        response = self.client.post(url, self.camera_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Camera.objects.count(), 1)
        self.assertEqual(Camera.objects.get().name, 'Test Camera')
        self.assertEqual(Camera.objects.get().status, 'online')
        
    @patch('cameras.validators.validate_camera_connection')
    def test_add_camera_unreachable(self, mock_validate):
        """Test adding an unreachable camera"""
        # Mock the camera validation to return False
        mock_validate.return_value = (False, 'offline')
        
        url = reverse('camera-list')
        response = self.client.post(url, self.camera_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Camera.objects.count(), 0)
        
    @patch('cameras.validators.validate_camera_connection')
    def test_check_camera_status(self, mock_validate):
        """Test checking camera status"""
        # Create a camera
        mock_validate.return_value = (True, 'online')
        camera = Camera.objects.create(
            user=self.user,
            name='Test Camera',
            ip_address='192.168.1.100',
            location='Test Location',
            status='online'
        )
        
        # Mock the camera validation to return offline
        mock_validate.return_value = (False, 'offline')
        
        url = reverse('camera-check-status', args=[camera.id])
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'offline')
        
        # Refresh from database
        camera.refresh_from_db()
        self.assertEqual(camera.status, 'offline')
