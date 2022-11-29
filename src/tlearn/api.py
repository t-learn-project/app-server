from ninja import Router, Schema
from django.shortcuts import get_object_or_404
# from django.db import connection
from .models import *
from typing import List
from datetime import *
import datetime as datka
from operator import itemgetter

router = Router()


@router.get("/card/study")
def get_cards_to_study(request, count: int):
    prog = CardUserProgress.objects.all()[:count]
    now_data = datka.datetime.now()
    response_0 = []
    response_not_0 = []
    for x in prog:
        card_translations = x.card.translation.all()
        total = (now_data - x.time_created).seconds
        if x.state.period >= 0 and total > x.state.period and x.state.period != -1:
            if x.state.period == 0:
                response_0.append({
                    'collection': x.card.collection.name,
                    'word': x.card.word,
                    'transcription': x.card.transcription,
                    'translation': [i.word for i in card_translations],
                    'type': x.card.type,
                    'status': x.state.period,
                })
            if x.state.period > 0:
                response_not_0.append({
                    'collection': x.card.collection.name,
                    'word': x.card.word,
                    'transcription': x.card.transcription,
                    'translation': [i.word for i in card_translations],
                    'type': x.card.type,
                    'status': x.state.period,
                })
    response = (sorted(response_not_0, key=itemgetter('status')) + response_0)[:count]
    return response


@router.post("/cards/study")
def handle_user_feedback(request, otvet: int, id_card: int, id_user: int):
    response = []
    down = CardUserProgress.objects.filter(card_id=id_card, user_id=id_user)
    check_step = 0
    for i in down:
        def append_progress(response):
            response.append({
                'id': i.id,
                'time_created': i.time_created,
                'penalty_step': i.penalty_step,
                'card_id': i.card_id,
                'state_id': i.state_id + 1,
                'user_id': i.user_id})

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

        if i.state_id >= 1 and otvet == 1 and i.penalty_step == False:
            for j in range(1, 8):
                if i.state_id == j:
                    employee = get_object_or_404(CardUserProgress, pk=i.id)
                    setattr(employee, 'state_id', j + 1)
                    employee.save()
                    append_progress(response)
                    if i.state_id == 8:
                        break

    return response


""" #Штрафной шаг
        if i.state_id>1:
            for j in range(1,8):
                if i.state_id==j:
                    if i.state_id >= 3 and i.state_id != check_step:
                        check_step = j
                        employee = get_object_or_404(CardUserProgress, pk=i.id)
                        setattr(employee, 'state_id', 2)
                        setattr(employee, 'penalty_step', True)
                        employee.save()
                        append_progress(response)

                    if i.penalty_step == True and otvet==1:

                        if i.state_id == 2 and i.state_id != check_step:
                            employee = get_object_or_404(CardUserProgress, pk=i.id)
                            setattr(employee, 'state_id', 3)
                            employee.save()
                            append_progress(response)

                        if i.state_id == 3 and i.state_id == check_step and i.penalty_step == True:
                            employee = get_object_or_404(CardUserProgress, pk=i.id)
                            setattr(employee, 'state_id', check_step+1)
                            setattr(employee, 'penalty_step', False)
                            employee.save()
                            append_progress(response)
                        
                                                    
        if i.state_id == 8:
                break  
    return response """


@router.get("/card/progress_get")
def get_progress(request):
    CardUserProgr_list = []
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
    return CardUserProgr_list


class Collection(Schema):
    name: str


class TranslationSetOut(Schema):
    id: int
    word: str


class CardOut(Schema):
    id: int
    collection: str
    word: str
    transcription: str
    translation: List[str]
    type: int


@router.get("/card/all", response=List[CardOut])
def get_all_cards(request):
    card_list = []
    card_set = Card.objects.all()
    for card in card_set:
        card_translations = card.translation.all()
        card_list.append({
            'id': card.id,
            'collection': card.collection.name,
            'word': card.word,
            'transcription': card.transcription,
            'translation': [i.word for i in card_translations],
            'type': card.type
        })
    return card_list


class CardIn(Schema):
    word: str
    transcription: str
    translation: List[str]
    type: int


class Statistics(Schema):
    user_id: int
    card_id: int
    state_id: int
    time_created: datetime
    penalty_step: bool


class CardCollectionIn(Schema):
    collection: str
    cards: List[CardIn]
    stata: List[Statistics]


@router.post("/card/add")
def create_card(request, payload: CardCollectionIn, id_user: int):
    collection = CardCollection.objects.create(name=payload.collection)
    for card in payload.cards:
        card_object = Card.objects.create(
            collection=collection,
            word=card.word,
            transcription=card.transcription,
            type=card.type
        )
        for translation in card.translation:
            Translation.objects.create(
                word=translation,
                card=card_object
            )
        id_state = 1
        CardUserProgress.objects.create(
            user_id=id_user,
            card_id=card_object.id,
            state_id=id_state,
            time_created=0,
            penalty_step=False,
        )
    return f'{card_object.word} с id = {card_object.id} Записано в базу данных!'
