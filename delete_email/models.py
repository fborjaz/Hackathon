from django.db import models

class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    deleted_emails_count = models.IntegerField(default=0)
    carbon_saved = models.FloatField(default=0.0)  # Gramos de CO₂ ahorrados
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.deleted_emails_count} emails eliminados - {self.carbon_saved} g CO₂ ahorrados"
