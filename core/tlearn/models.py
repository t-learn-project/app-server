from django.db import models

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(blank=True, max_length=255)
    translation = models.CharField(blank=True, max_length=255)
    collection = models.ForeignKey('Collection', on_delete=models.PROTECT)

class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, max_length=255)

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(blank=True, max_length=255)
    active_collection = models.ForeignKey('Collection',  on_delete=models.PROTECT)

class CardProgress(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.ForeignKey('User',  on_delete=models.PROTECT)
    collection = models.ForeignKey('Collection',  on_delete=models.PROTECT)
    card = models.ForeignKey('Card',  on_delete=models.PROTECT)
    rotation = models.ForeignKey('Rotation',  on_delete=models.PROTECT)
    time_updated = models.DateTimeField(auto_now=True)

class Rotation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, max_length=255)
    period = models.IntegerField()
