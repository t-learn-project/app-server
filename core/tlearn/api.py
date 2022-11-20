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
        penalty_step = payload.penalty_step
        )

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
    for i in range(len(CardUserProgr_list)):
        if CardUserProgr_list[i]['state']!=0 and CardUserProgr_list[i]['total']>CardUserProgr_list[i]['state']:
            return CardUserProgr_list[i] 
            
            

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



""" from time import gmtime, strftime
hours = (int(strftime("%H", gmtime())))*3600
minutes = (int(strftime("%M", gmtime())))*60
seconds = int(strftime("%S", gmtime()))

summa_seconds = hours+minutes+seconds


showtime = strftime("%H:%M:%S", gmtime())

print(showtime, summa_seconds) """











""" class CardOut(Schema):
    id: int
    word: str
    translation: str

class CardsOut(Schema):
    count: int
    cards: List[CardOut]

class CardIn(Schema):
    collection_id: int
    word: str
    translation: str

@router.get("/card/all", response=List[CardOut])
def get_all_cards(request):
    card_list = Card.objects.all()
    return card_list

@router.post("/card/add")
def create_card(request, payload: CardIn):
    new_card = Card.objects.create(
        collection_id = payload.collection_id,
        word = payload.word,
        translation = payload.translation
    )
    return "Успешно!!!!!!!"
    
@router.post("/card/addlist")
def create_cards(request, payload: List[CardIn]):
    for card in payload:
        new_card = Card.objects.create(
            collection_id = card.collection_id,
            word = card.word,
            translation = card.translation
        )
    return "Успешно!!!!!!!"

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