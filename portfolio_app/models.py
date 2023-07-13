from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.TextField()


class Institution(models.Model):
    TYPES = (
        (0, "Fundacja"),
        (1, "Organizacja pozarządowa"),
        (2, "Zbiórka lokalna"),
    )

    name = models.TextField()
    description = models.TextField()
    types = models.IntegerField(choices=TYPES, default=0)
    categories = models.ManyToManyField(Category)


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.TextField()
    city = models.TextField()
    zip_code = models.TextField()
    pick_up_date = models.DateField()
    pick_up_time = models.DateField()
    pick_up_comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
