from django.db import models

# Create your models here.
class Compound(models.Model):
    compound_id = models.CharField("compound_id", max_length=30, default="")
    smiles = models.CharField("smiles", max_length = 180, default="")
