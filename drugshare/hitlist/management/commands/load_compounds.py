"""command to load data into website"""
import os
import re
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from hitlist.models import Compound

  
def populate_compounds(row, required_fields):
    try:
        entry = Compound()
        for i in required_fields:
            print(i.verbose_name, row)
            print("HIHIHI")
            setattr(entry, i.name, row[i.verbose_name])
            print("AM HERE") 
            entry.save()
    except Exception as error_message:
        print("BLA")
        print(error_message)



class Command(BaseCommand):
    help = "command to load hitlist"

    def add_arguments(self, parser):
        parser.add_argument('infile', type=str, help="input file")
      

    def handle(self, *args, **kwargs):
        with open(os.path.join(os.getcwd(), kwargs['infile'])) as csvfile:
            reader = pd.read_csv(csvfile)
            required_fields = Compound._meta.get_fields()
            for _, row in reader.iterrows():
                populate_compounds(row, required_fields)
