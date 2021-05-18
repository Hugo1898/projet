from django.contrib.auth.models import User
from django.db import models

class Communaute(models.Model):
    nom = models.CharField(max_length=200)
    abonnes = models.ManyToManyField(User, related_name="communautes")

    class Meta:
        verbose_name = "Communaute"

    def __str__(self):
        return self.nom

