import django_tables2 as tables
from .models import Compound
from django.utils.html import format_html

class CompoundTable(tables.Table):
   
    crystal_id = tables.Column()
    def render_compound_smiles(self, value, record):
        return format_html('<canvas class=myCanvas data-smiles="{}"></canvas>', record.compound_smiles)
      #  return format_html("<b>{} {}</b>", value, record.compound_smiles)
    class Meta:
        model = Compound
        fields = ('crystal_id', 'datasetcluster', 'library_name','compound_smiles')
         


