# Generated by Django 4.1 on 2024-01-19 03:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("decklist", "0018_alter_combolist_combo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="combolist",
            name="combo",
        ),
        migrations.AlterField(
            model_name="cardlist",
            name="card_amount",
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)]),
        ),
        migrations.AlterField(
            model_name="cardlist",
            name="card_classification",
            field=models.CharField(
                blank=True,
                choices=[("Starter", "Starter"), ("Garnet", "Garnet")],
                max_length=50,
            ),
        ),
    ]
