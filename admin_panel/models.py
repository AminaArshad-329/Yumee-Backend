from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

class ForgetPasswordTokens(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Packages(models.Model):
    PACKAGE = (
        (
            ('Classic', 'Classic'),
            ('VIP', 'VIP'),
            ('Classic Plus', 'Classic Plus'),
            ('VIP Plus', 'VIP Plus')
        )
    )
    PACKAGE_TIME = (
        (
            ('1 Month', '1 Month'),
            ('3 Month', '3 Month'),
            ('6 Month', '6 Month'),
            ('15 Days Trial', '15 Days Trial')
        )
    )

    name = models.CharField(max_length=100, choices=PACKAGE)
    price = models.PositiveIntegerField()
    duration = models.CharField(max_length=100, choices=PACKAGE_TIME)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
