from django.db import models

class CardCollection(models.Model):
    name = models.CharField(max_length=255)

class TranslationSet(models.Model):
    pass

class CardProgressStep(models.Model):
    time_created = models.DateTimeField(auto_now=True)
    previous_step = models.OneToOneField(to='self', null=True, on_delete=models.SET_NULL)

class User(models.Model):
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    active_collection = models.OneToOneField(CardCollection, on_delete = models.CASCADE)

class Card(models.Model):
    collection = models.ForeignKey(CardCollection, on_delete = models.CASCADE)
    word = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    translation = models.OneToOneField(TranslationSet, on_delete = models.CASCADE)

class CardUserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    current_step = models.OneToOneField(CardProgressStep, related_name = '+', on_delete=models.CASCADE)
    fail_step = models.OneToOneField(CardProgressStep, related_name = '+', on_delete=models.CASCADE)

class CardState(models.Model):
    name = models.CharField(max_length=255)
    period = models.IntegerField()

class Translation(models.Model):
    word = models.CharField(max_length=255)
    set = models.ForeignKey(TranslationSet, on_delete=models.CASCADE)