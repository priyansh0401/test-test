import random
import threading
import time
import json
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from cameras.models import Camera
from .models import Alert

def generate_random_alert():
    """
    Generate a random alert for a random camera
    """
    # Get all online cameras
    cameras = Camera.objects.filter(status='online')
    if not cameras.exists():
        return None
    
    # Select a random camera
    camera = random.choice(cameras)
    
    # Select a random alert type
    alert_type = random.choice(['Motion', 'Crying'])
    
    # Generate a message
    if alert_type == 'Motion':
        message = f"Motion detected at {camera.location}"
    else:
        message = f"Crying sound detected at {camera.location}"
    
    # Create the alert
    with transaction.atomic():
        alert = Alert.objects.create(
            camera=camera,
            alert_type=alert_type,
            message=message
        )
    
    # Return the alert data
    return {
        'id': alert.id,
        'camera_id': camera.id,
        'camera_name': camera.name,
        'alert_type': alert_type,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }

def send_alert_to_websocket(alert_data):
    """
    Send the alert to the WebSocket
    """
    if not alert_data:
        return
    
    # Get the channel layer
    channel_layer = get_channel_layer()
    
    # Get the user ID
    user_id = Camera.objects.get(id=alert_data['camera_id']).user_id
    
    # Send the alert to the user's group
    async_to_sync(channel_layer.group_send)(
        f'alerts_{user_id}',
        {
            'type': 'alert_message',
            'message': alert_data
        }
    )

def alert_simulator():
    """
    Simulate alerts at random intervals
    """
    while True:
        # Sleep for a random interval (5-30 seconds)
        time.sleep(random.randint(5, 30))
        
        # Generate a random alert
        alert_data = generate_random_alert()
        
        # Send the alert to the WebSocket
        if alert_data:
            send_alert_to_websocket(alert_data)

def start():
    """
    Start the alert simulator in a background thread
    """
    thread = threading.Thread(target=alert_simulator, daemon=True)
    thread.start()
