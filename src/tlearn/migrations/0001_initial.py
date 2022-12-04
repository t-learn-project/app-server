# Generated by Django 4.1.3 on 2022-12-04 20:40

from django.db import migrations, models
import django.db.models.deletion
import django_enumfield.db.fields
import tlearn.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('transcription', models.CharField(max_length=255)),
                ('type', django_enumfield.db.fields.EnumField(enum=tlearn.models.Type)),
            ],
        ),
        migrations.CreateModel(
            name='CardCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('period', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('active_collection', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tlearn.cardcollection')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translation', to='tlearn.card')),
            ],
        ),
        migrations.CreateModel(
            name='CardUserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now=True)),
                ('penalty_step', models.BooleanField()),
                ('penalty_state_id', models.IntegerField(default=0)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tlearn.card')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tlearn.state')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tlearn.user')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tlearn.cardcollection'),
        ),
    ]
