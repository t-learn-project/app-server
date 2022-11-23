from django.db import models
from django_enumfield import enum
from django.utils import timezone
""" from django.utils.timezone import utc
import datetime """


class Type(enum.Enum):
    NOUN = 0,        
    PRONOUN = 1,     
    VERB = 2,        
    ADJECTIVE = 3,   
    ADVERB = 4,     
    PREPOSITION = 5, 
    CONJUNCTION = 6, 
    INTERJECTION = 7

class State(enum.Enum):
    Новое_Слово = 0,        
    Через_5_Минут = 300,     
    Через_1_Час = 3600,        
    Через_1_День = 86400,   
    Через_1_Неделю = 604800,     
    Через_1_Месяц = 2419200, 
    Через_3_Месяца = 7257600, 
    Слово_Выучено = -1,
    Уже_Знает = -2

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
    type = enum.EnumField(Type)

    def __str__(self):
        return self.word

class CardUserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    state = enum.EnumField(State)
    time_created = models.DateTimeField(auto_now=True)
    penalty_step = models.BooleanField()


class Translation(models.Model):
    word = models.CharField(max_length=255)
    card = models.ForeignKey(Card, related_name='translation', on_delete=models.CASCADE)

    def __str__(self):
        return self.word
    
    
""" class ForTestTimeIn(models.Model):
    created_time_in = models.DateTimeField(auto_now=True)#У меня здесь записано время ответа фронта
    def get_time_diff(self):
        if self.created_time:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            TotalTime = now - self.created_time
            return TotalTime.total_seconds() 

class ForTestTimeOut(models.Model):
    created_time_out = models.DateTimeField(auto_now=True)
 """

'''Type {
  NOUN = 0, // rus: существительное
  PRONOUN = 1,     // rus: местоимение
  VERB = 2,        // rus: глагол
  ADJECTIVE = 3,   // rus: прилагательное
  ADVERB = 4,      // rus: наречие
  PREPOSITION = 5, // rus: предлог
  CONJUNCTION = 6, // rus: союз
  INTERJECTION = 7 // rus: междометие
}'''

