# Generated by Django 4.2.16 on 2024-11-13 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_quantity_ingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='time_preparations',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='picture',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
    ]
