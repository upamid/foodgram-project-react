import json

from django.conf import settings
from django.core.management import BaseCommand
from django.core import management
from django.core.management.commands import loaddata

from recipes.models import Recipe


class Command(BaseCommand):
    help = "load data"
    fixture_filename = 'ingerdients.json'
        
    def handle(self, path, **options):
        management.call_command('loaddata', settings.STATIC_ROOT+'/ingerdients.json')
