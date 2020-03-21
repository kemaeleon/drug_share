"""command to load data into website"""
import os
import re
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from hitlist.models import Compound

class Command(BaseCommand):
    help = "command to load hitlist"

    def add_arguments(self, parser):
        parser.add_argument('infile', type=str, help="input file")

    def handle(self, *args, **kwargs):
        with open(os.path.join(os.getcwd(), kwargs['infile'])) as csvfile:
            reader = pd.read_csv(csvfile)
            for _, row in reader.iterrows():
                print(row)
