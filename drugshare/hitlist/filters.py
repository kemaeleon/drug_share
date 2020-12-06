"""filter fields in tables on regulatome website"""
import django_filters
from .models import Compound

class CompoundFilter(django_filters.FilterSet):
    """filter gene table"""
    class Meta:
        model = Compound
        fields = {
            'crystal_id': ['exact'],
            'compound_smiles': ['contains'],
        }

