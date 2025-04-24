from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model with additional fields
    """
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    
    def __str__(self):
        return self.username
