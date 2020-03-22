from django.db import models

# Create your models here.
class Compound(models.Model):
    crystal_id = models.CharField("Crystal ID", max_length=30, primary_key=True, blank=False, null=False, default='')
    datasetcluster = models.IntegerField("DatasetCluster", blank=False, null=False, default=0)
    library_name = models.CharField("Library Name", blank=True, null=True, max_length=30)
    compound_smiles = models.CharField("Compound SMILES", blank=False, null=False, max_length = 180, default="")
    modified_compound_smiles = models.CharField("Modified Compound Smiles", blank=False, null=True,  max_length = 180)
    compoundcode = models.CharField("CompoundCode", blank=True, null=True, max_length=30)
    status = models.CharField("Status", blank=True, null=True, max_length=30)
    site = models.CharField("Site", blank=True, null=True, max_length=30)
    initial_occupancy_estimate = models.DecimalField("initial occupancy estimate", max_digits=4, decimal_places=2, blank=True, null=True, default=0)
    peak_height_z_value = models.DecimalField("peak-height z-value", max_digits=4, decimal_places=2, blank=True, null=True, default=0)
    map_resol = models.DecimalField("Map Resol", max_digits=4, decimal_places=2, blank=True, null=True, default=0)
    confidence_annotation = models.CharField("Confidence annotation", max_length=5, blank=True, default='')

