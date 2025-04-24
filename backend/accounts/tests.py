from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth_register')
        self.token_url = reverse('token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        
    def test_user_login(self):
        """Test user login with JWT"""
        # Create a user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        # Login
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_password_reset_request(self):
        """Test password reset request"""
        # Create a user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        # Request password reset
        url = reverse('password_reset_request')
        response = self.client.post(url, {'email': 'test@example.com'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
