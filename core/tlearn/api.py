from ninja import Router, Schema
from .models import *
from typing import List
from datetime import *
import datetime as datka

router = Router()

class Statistics(Schema):
    user_id: int
    card_id: int
    state: int 
    time_created: datetime
    penalty_step: bool

class Statistics_For_GET(Schema):
    user_id: int
    card_id: int
    state: int 
    time_created: datetime
    penalty_step: bool
    now_time: datetime
    total: datka.timedelta

@router.post("/card/progress_post")
def progress_post(request, payload: Statistics, otvet: int):
    if otvet==0:
        CardUserProgress.objects.create(
        user_id = payload.user_id,
        card_id = payload.card_id,
        state = payload.state,
        time_created = payload.time_created,
        penalty_step = payload.penalty_step)
    else:
        return 'Вы знаете слово!'

@router.get("/card/progress_get")
def get_all_progress(request):
    CardUserProgr_list=[]
    data = datka.datetime.now()
    CardUserProgr_set = CardUserProgress.objects.all()
    for stat in CardUserProgr_set:
        CardUserProgr_list.append({
            'user_id': stat.user_id,
            'card_id': stat.card_id,
            'state': stat.state,
            'time_created': stat.time_created,
            'penalty_step': stat.penalty_step,
            'now_time': data,
            'total': (data - stat.time_created).seconds,
        })
    response = [] 
    for i in CardUserProgr_list:
        if i['state']!=0 and i['total'] > i['state']:
            response.append(i)
    return response

@router.put("/card/progress_get")
def update_carduserprogress(request, otvet: str):
    CardUserProgr_list=[]
    states = [0, 300, 3600, 86400, 604800, 2419200, 7257600, -1]
    data = datka.datetime.now()
    CardUserProgr_set = CardUserProgress.objects.all()
    for stat in CardUserProgr_set:
        CardUserProgr_list.append({
            'user_id': stat.user_id,
            'card_id': stat.card_id,
            'state': stat.state,
            'time_created': stat.time_created,
            'penalty_step': stat.penalty_step,
            'now_time': data,
            'total': (data - stat.time_created).seconds,
        })
    dost = CardUserProgress.objects.all()
    response = []
    for i in CardUserProgr_list:
        for j in range(len(states)-1):
            if i['state']==states[j] and i['state']>0 and i['total'] > i['state'] and otvet == 'Да':
                setattr(dost, 'state', states[j+1])
                dost.save()
                response.append(i)
    return response
                
@router.get("/card/get_from_state")
def get_all_cards_from_states(request, count: int):
    CardUserProgr_list=[]
    CardUserProgr_set = CardUserProgress.objects.all()
    for stat in CardUserProgr_set:
        CardUserProgr_list.append({
            'user_id': stat.user_id,
            'card_id': stat.card_id,
            'state': stat.state,
            'time_created': stat.time_created,
            'penalty_step': stat.penalty_step,
        })
    CardList = []
    CardSet = Card.objects.all()
    for card in CardSet:
        card_translations = card.translation.all()
        CardList.append({
            'id': card.id,
            'collection': card.collection.name,
            'word': card.word,
            'transcription': card.transcription,
            'translation': [i.word for i in card_translations],
            'type': card.type
        })
    otvet = []
    for i in CardUserProgr_list:
        for j in CardList:
            if i['card_id']==j['id']:
                otvet.append(j)
    return otvet
""" @router.get("/card/count", response=CardsOut)
def get_cards(request, count: int):
    card_list = Card.objects.all()[:count]
    return {
        'count': len(card_list),
        'cards': list(card_list)
    }  """

class Collection(Schema): 
    name: str

class TranslationSetOut(Schema):
    id: int 
    word: str

class CardOut(Schema):
    collection: str
    word: str
    transcription: str
    translation: List[str]
    type: int

class CardIn(Schema):
    word: str
    transcription: str
    translation: List[str]
    type: int

class CardCollectionIn(Schema):
    collection: str
    cards: List[CardIn]    


@router.get("/card/all", response=List[CardOut])
def get_all_cards(request):
    card_list=[]
    card_set = Card.objects.all()
    for card in card_set:
        card_translations = card.translation.all()
        card_list.append({
            'collection': card.collection.name,
            'word': card.word,
            'transcription': card.transcription,
            'translation': [i.word for i in card_translations],
            'type': card.type
        })
    return card_list
 
@router.post("/card/add")
def create_cards(request, payload: CardCollectionIn):
    collection = CardCollection.objects.create(name=payload.collection)
    for card in payload.cards:
        card_object = Card.objects.create(
            collection=collection,
            word = card.word,
            transcription = card.transcription,
            type = card.type
                )
        for translation in card.translation:
            Translation.objects.create(
                word = translation,
                card = card_object
                )
    return f'{card} Записано в базу данных!'

@router.get("/card/count", response=List[CardOut])
def get_cards(request, count: int):
    card_list=[]
    card_set = Card.objects.all()[:count]
    for card in card_set:
        card_translations = card.translation.all()
        card_list.append({
            'collection': card.collection.name,
            'word': card.word,
            'transcription': card.transcription,
            'translation': [i.word for i in card_translations],
            'type': card.type
        })
    return card_list









""" 
@router.get("/card/count", response=CardsOut)
def get_cards(request, count: int):
    card_list = Card.objects.all()[:count]
    return {
        'count': len(card_list),
        'cards': list(card_list)
    } """
"""
У карточки есть стейт, который определяет на какой станции находится слово
По дефолту этот стейт равен 0, затем он обновляется, если пользователь нажал, что не знает слово 
"""


""" 
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department)
    birthdate = models.DateField(null=True, blank=True)

class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    birthdate: date = None

@api.put("/employees/{employee_id}")
def update_employee(request, state: int, payload: Statistics):
    employee = Card(Employee, id=state)
    for attr, value in payload.dict().items():
        setattr(employee, attr, value)
    employee.save()
    return {"success": True}








 """


