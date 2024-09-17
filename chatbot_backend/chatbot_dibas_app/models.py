from django.db import models

# Create your models here.
# chatbot_dibas_app/models.py
from django.db import models

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True)  # Optional: store the appointment date
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.name}"
