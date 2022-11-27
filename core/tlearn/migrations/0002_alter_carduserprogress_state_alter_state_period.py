# Generated by Django 4.1.3 on 2022-11-27 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tlearn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carduserprogress',
            name='state',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='tlearn.state'),
        ),
        migrations.AlterField(
            model_name='state',
            name='period',
            field=models.IntegerField(),
        ),
    ]