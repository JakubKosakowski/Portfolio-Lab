from django.db import models


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
