# Generated by Django 4.1.3 on 2022-11-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tlearn", "0003_alter_collection_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collection",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
