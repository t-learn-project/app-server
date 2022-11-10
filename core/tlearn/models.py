from django.db import models

class CardCollection(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class User(models.Model):
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    active_collection = models.OneToOneField(CardCollection, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Card(models.Model):
    collection = models.ForeignKey(CardCollection, on_delete = models.CASCADE)
    word = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)

    def __str__(self):
        return self.word


class CardProgressStep(models.Model):
    time_created = models.DateTimeField(auto_now=True)
    card_progress = models.ForeignKey('CardUserProgress', on_delete=models.CASCADE)

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
    card = models.ForeignKey(Card, related_name='translation', on_delete=models.CASCADE)

    def __str__(self):
        return self.word