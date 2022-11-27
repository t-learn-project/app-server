from ninja import Router, Schema
from django.shortcuts import get_object_or_404
#from django.db import connection
from .models import *
from typing import List
from datetime import *
import datetime as datka
from operator import itemgetter

router = Router()
""" @router.get("/card/progress_get")
def get_all_progress(request):
    CardUserProgr_list=[]
    data = datka.datetime.now()
    CardUserProgr_set = CardUserProgress.objects.all()
    for stat in CardUserProgr_set:
        CardUserProgr_list.append({
            'user_id': stat.user_id,
            'card_id': stat.card_id,
            'period': stat.state.period,
            'time_created': stat.time_created,
            'penalty_step': stat.penalty_step,
            'now_time': data,
            'total': (data - stat.time_created).seconds,
        })
    response = [] 
    for i in CardUserProgr_list:
        if i['period']>=0 and i['total'] > i['period'] :
            response.append(i)
    return response """

@router.get("/card/card_in_progress")
def get_card_in_progress(request, count: int):
    prog = CardUserProgress.objects.all()[:count]
    now_data = datka.datetime.now()
    response_0 = []
    response_not_0 = []
    for x in prog:
        card_translations = x.card.translation.all()
        time_created =  x.time_created
        total = (now_data - x.time_created).seconds
        if x.state.period>=0 and total > x.state.period and x.state.period != -1:
            if x.state.period == 0: 
                response_0.append({
                    'collection': x.card.collection.name,
                    'word': x.card.word,
                    'transcription': x.card.transcription,
                    'translation': [i.word for i in card_translations],
                    'type': x.card.type,
                    'status': x.state.period,
                    })
            if x.state.period>0:
                response_not_0.append({
                    'collection': x.card.collection.name,
                    'word': x.card.word,
                    'transcription': x.card.transcription,
                    'translation': [i.word for i in card_translations],
                    'type': x.card.type,
                    'status': x.state.period,
                    })
    response =  sorted(response_not_0, key=itemgetter('status'))+response_0
    return response
    

class Statistics(Schema):
    user_id: int
    card_id: int
    state_id: int
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
def progress_post(request, otvet: int, id_card: int, id_user: int, payload: Statistics_For_GET):
    response = []
    down = CardUserProgress.objects.filter(card_id = id_card, user_id=id_user)
    data = datka.datetime.now()
        
    for i in down:

        if i.state_id == 1 and otvet == 1 and i.penalty_step == False:
            employee = get_object_or_404(CardUserProgress, pk=i.id)
            setattr(employee, 'state_id', 9)
            employee.save()
            return 'Вы уже знаете это слово'

        if i.state_id == 1 and otvet == 0:
            employee = get_object_or_404(CardUserProgress, pk=i.id)
            setattr(employee, 'state_id', 2)
            employee.save()
            return 'Слово попало в ротацию'

        if i.state_id>=1 and otvet == 1:
            for j in range(8):
                if i.state_id==j:
                    employee = get_object_or_404(CardUserProgress, pk=i.id)
                    setattr(employee, 'state_id', j+1)
                    setattr(employee, 'penalty_step', False)
                    employee.save()    
                    response.append({
                            'id': i.id,
                            'time_created': i.time_created,
                            'penalty_step': i.penalty_step,
                            'card_id': i.card_id,
                            'state_id': i.state_id+1,
                            'user_id': i.user_id
                    })
                    if i.state_id == 8:
                        break

        #Штрафной шаг
        if otvet == 0 and i.state_id>1:
            for j in range(8):
                if i.state_id==j:
                    if i.state_id >= 3:
                        employee = get_object_or_404(CardUserProgress, pk=i.id)
                        setattr(employee, 'state_id', j-2)
                        setattr(employee, 'penalty_step', True)
                        employee.save()    
                        response.append({
                                'id': i.id,
                                'time_created': i.time_created,
                                'penalty_step': i.penalty_step,
                                'card_id': i.card_id,
                                'state_id': i.state_id+1,
                                'user_id': i.user_id
                        })
                    if i.state_id == 8:
                        break  

    return response
    

@router.get("/card/progress_get")
def get_all_progress(request):
    CardUserProgr_list=[]
    data = datka.datetime.now()
    CardUserProgr_set = CardUserProgress.objects.all()
    for stat in CardUserProgr_set:
        CardUserProgr_list.append({
            'user_id': stat.user_id,
            'card_id': stat.card_id,
            'period': stat.state.period,
            'time_created': stat.time_created,
            'penalty_step': stat.penalty_step,
            'now_time': data,
            'total': (data - stat.time_created).seconds,
        })
    response = [] 
    for i in CardUserProgr_list:
        if i['period']>=0 and i['total'] > i['period'] :
            response.append(i)
    return response

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
    stata: List[Statistics] 

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
    id_state = 1
    data = datka.datetime.now()
    CardUserProgress.objects.create(
            user_id = 1,
            card_id = 17,
            state_id = id_state,
            time_created = 0,
            penalty_step = False,
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




""" @router.post("/card/progress_post")
def progress_post(request, otvet: int, id_card: int, id_user: int):
    response = []
    down = CardUserProgress.objects.filter(card_id = id_card, user_id=id_user)
    for i in down:
        employee = get_object_or_404(CardUserProgress, pk=i.id)
        if i.state_id == 1 and otvet == 1:
            setattr(employee, 'state_id', 9)
            employee.save()
        if otvet == 1 and i.state_id>0:
            for j in range(8):
                if i.state_id==j:
                    setattr(employee, 'state_id', j+1)
                    employee.save()    
                    response.append({
                    'id': i.id,
                    'time_created': i.time_created,
                    'penalty_step': i.penalty_step,
                    'card_id': i.card_id,
                    'state_id': i.state_id,
                    'user_id': i.user_id})
                    if i.state_id == 8:
                        break
        if otvet == 0 and i.state_id>0:
            for j in range(8):
                if i.state_id==j:
                    if i.state_id >= 3:
                        setattr(employee, 'state_id', j-2)
                        setattr(employee, 'penalty_step', True)
                        employee.save()    
                        response.append({
                        'id': i.id,
                        'time_created': i.time_created,
                        'penalty_step': i.penalty_step,
                        'card_id': i.card_id,
                        'state_id': i.state_id,
                        'user_id': i.user_id})
                    elif i.state_id == 8:
                        break
    return response """