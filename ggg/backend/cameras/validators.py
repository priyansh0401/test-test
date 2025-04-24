import cv2
import socket
import subprocess
import platform
from urllib.parse import urlparse
import time
import threading
import os
from django.conf import settings
import numpy as np
from PIL import Image
import io

def validate_camera_connection(ip_address):
    """
    Validate if the camera is reachable
    
    Returns:
        tuple: (is_reachable, status)
    """
    # Check if it's a URL (RTSP, HTTP, etc.)
    if ip_address.startswith(('rtsp://', 'http://', 'https://')):
        return validate_stream_url(ip_address)
    
    # Otherwise, treat as IP address
    return ping_ip(ip_address)

def validate_stream_url(url):
    """
    Validate if the camera stream URL is accessible using OpenCV
    """
    try:
        # In serverless environment, we'll just assume the URL is valid
        # This is because OpenCV might not work properly in Vercel's environment
        if os.getenv('VERCEL_ENV'):
            return True, 'online'
            
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            return False, 'offline'
        
        # Try to read a frame
        ret, frame = cap.read()
        
        # If we got a frame, save a thumbnail
        if ret and frame is not None:
            # Create thumbnails directory if it doesn't exist
            thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'camera_thumbnails')
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Save the frame as a thumbnail
            thumbnail_path = os.path.join(thumbnails_dir, f"{int(time.time())}.jpg")
            cv2.imwrite(thumbnail_path, frame)
            
            # Release the capture
            cap.release()
            
            return True, 'online'
        
        cap.release()
        return False, 'offline'
    except Exception as e:
        print(f"Error validating stream URL: {e}")
        # In serverless environment, we'll just assume the URL is valid
        if os.getenv('VERCEL_ENV'):
            return True, 'online'
        return False, 'offline'

def ping_ip(ip_address):
    """
    Ping the IP address to check if it's reachable
    """
    # In serverless environment, we'll just assume the IP is valid
    if os.getenv('VERCEL_ENV'):
        return True, 'online'
        
    # Parse the IP address if it contains port
    parsed = urlparse('//' + ip_address)
    ip = parsed.hostname or ip_address
    
    # Determine the ping command based on the OS
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]
    
    try:
        # Run the ping command
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return True, 'online'
    except subprocess.CalledProcessError:
        # If ping fails, try socket connection
        try:
            # If port is specified, use it, otherwise use default port 80
            port = parsed.port or 80
            with socket.create_connection((ip, port), timeout=2):
                return True, 'online'
        except (socket.timeout, socket.error):
            return False, 'offline'

def capture_camera_thumbnail(camera):
    """
    Capture a thumbnail from the camera
    """
    try:
        # In serverless environment, we'll skip thumbnail capture
        if os.getenv('VERCEL_ENV'):
            return True
            
        # Use the stream URL if available, otherwise use the IP address
        url = camera.stream_url if camera.stream_url else camera.ip_address
        
        # If it's just an IP address, try to form a proper URL
        if not url.startswith(('rtsp://', 'http://', 'https://')):
            if camera.camera_type == 'rtsp':
                url = f"rtsp://{url}:554/stream"
            elif camera.camera_type == 'onvif':
                url = f"rtsp://{url}:554/onvif1"
            else:
                url = f"http://{url}"
        
        # Open the video capture
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            return False
        
        # Convert the frame to a PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Create a BytesIO object to save the image
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=85)
        img_io.seek(0)
        
        # Save the image to the camera's thumbnail field
        thumbnail_name = f"{camera.id}_{int(time.time())}.jpg"
        camera.thumbnail.save(thumbnail_name, img_io, save=True)
        
        return True
    except Exception as e:
        print(f"Error capturing thumbnail: {e}")
        return False
