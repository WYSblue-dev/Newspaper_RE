from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=False)
    # added the email field to model and made it required.
    email = models.EmailField(blank=False)
