from django.shortcuts import render
from .tables import CompoundTable
from .models import Compound
from django_tables2 import RequestConfig, SingleTableMixin
from django_tables2.export.views import ExportMixin
from django_filters.views import FilterView
from .filters import CompoundFilter

# Create your views here.

def hit(request):
    return render(request, 'hitlist.html')

def home(request):
    return render(request, 'hitlist.html')

def prometheus(request):
    return render(request, 'prometheus.html')

class CompoundTableView(ExportMixin, SingleTableMixin,FilterView):
    model = Compound
    table_class = CompoundTable
    filterset_class = CompoundFilter
    template_name = "compound_table.html"
    export_formats = ()


