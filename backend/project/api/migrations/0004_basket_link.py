# Generated by Django 4.2.16 on 2024-11-18 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_basket_basket_unique_shopping_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='link',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Ссылка'),
        ),
    ]
