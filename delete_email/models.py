from django.db import models

class UserProfile(models.Model):
    email = models.EmailField(unique=True)  # Campo para almacenar el correo electrónico
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return self.email
