from django.db import models
from django.contrib.auth.models import User

class UserRole(models.Model):
    ROLE_CHOICES = (
        ('gerente', 'Gerente'),
        ('administrador', 'Administrador'),
        ('supervisor', 'Supervisor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"