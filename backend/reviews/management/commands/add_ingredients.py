import json
from django.core.management.base import BaseCommand
from reviews.models import Ingredient


class Command(BaseCommand):
    help = "Загрузить ингредиенты из файла JSON"

    def handle(self, *args, **kwargs):
        with open('ingredients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
        print(("Ингредиенты успешно загружены!"))
