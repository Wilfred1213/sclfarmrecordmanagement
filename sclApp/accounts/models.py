from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add your custom fields here
    department = models.CharField(max_length=50, choices=[
        ('GREENHOUSE', 'Greenhouse'),
        ('LIVESTOCK', 'Livestock'),
        ('FACTORY', 'Factory'),
        ('INVENTORY', 'Store'),
        ('ADMIN', 'Administration'),
    ], default='ADMIN')
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    staff_id = models.CharField(max_length=10, unique=True, null=True)

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return f"{self.username} ({self.get_department_display()})"