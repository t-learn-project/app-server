from django.db import models

class Card_Collection(models.Model):
    name = models.CharField(blank=True, max_length=255)

class Translation_Set(models.Model):
    id = models.BigAutoField(primary_key=True)

class Card_Progress_Step(models.Model):
    time_created = models.DateTimeField(auto_now=True)
    previous_step = models.IntegerField()

class User(models.Model):
    email = models.CharField(blank=True, max_length=255)
    first_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    active_collection = models.OneToOneField(Card_Collection, on_delete = models.CASCADE)

class Card(models.Model):
    collection = models.ForeignKey(Card_Collection, on_delete = models.CASCADE)
    word = models.CharField(blank=True, max_length=255)
    transcription = models.CharField(blank=True, max_length=255)
    translation = models.OneToOneField(Translation_Set, on_delete = models.CASCADE)

class Card_User_Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    #current_step = models.OneToOneField(Card_Progress_Step, on_delete=models.CASCADE)
    fail_step = models.OneToOneField(Card_Progress_Step, on_delete=models.CASCADE)

class Card_State(models.Model):
    name = models.CharField(blank=True, max_length=255)
    period = models.IntegerField()

class Translation(models.Model):
    word = models.CharField(blank=True, max_length=255)
    set = models.ForeignKey(Translation_Set, on_delete=models.CASCADE)