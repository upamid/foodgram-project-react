import json
import os

from django.core.management import BaseCommand

from recipes.models import Ingredient

fixture_dir = ''
fixture_filename = 'ingredients.json'


class Command(BaseCommand):
    help = "load data"

    def handle(self, *args, **options):
        fixture_file = os.path.join(fixture_dir, fixture_filename)
        print(fixture_file)
        f = open(fixture_file,)
        my_json_obj = json.load(f)
        for title in my_json_obj:
            Ingredient.objects.create(
                name=title['name'],
                measurement_unit=title['measurement_unit']
                )
