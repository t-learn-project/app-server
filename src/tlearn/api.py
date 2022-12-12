from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from .models import *
from typing import List
from datetime import *
import datetime as datka
from ninja.security import django_auth
from .models_for_api import *

router = Router()

""" @router.get("/cards/statistics", auth=AuthBearer())
def returns_statistics(request):
    id_user = request.auth
    progress = CardUserProgress.objects.filter(user_id = id_user)
    not_in_progress = len(progress.exclude(state_id__in = [2,3,4,5,6,7]))
    in_progress = len(progress.exclude(state_id__in = [1,8,9]))
    is_learned = len(progress.filter(state_id = 8))
    already_learned = len(progress.filter(state_id = 9))
    return f'Кол-во в ротации: {in_progress}; ' \
           f'Кол-во не в ротации: {not_in_progress}; ' \
           f'Кол-во выученных: {is_learned}; ' \
           f'Кол-во заранее выученных: {already_learned}; ' """

@router.get("/cards/study", auth=AuthBearer())
def returns_cards_for_study(request, count: int):
    id_user = request.auth
    progress = CardUserProgress.objects.filter(user_id = id_user)[:count]
    def AppendCards(list, arg, id):
        list.append({
                'id': id,
                'collection': arg.collection.name,
                'word': arg.word,
                'transcription': arg.transcription,
                'translation': [i.word for i in card_translations],
                'type': arg.type
                })

    collection_user = User.objects.get(id = id_user)
    all_new_cards = Card.objects.exclude(id__in = CardUserProgress.objects.values_list('id'))#Карточки, которых нету в ротации
    now_data = datka.datetime.now()

    new_cards = []
    cards_in_rotations = []
    for x in progress:
        card_translations = x.card.translation.all() 
        active_collection_id = collection_user.active_collection_id
        total = (now_data - x.time_created).seconds
        if x.state.period>=0 and total > x.state.period and x.card.collection.id == active_collection_id:

            #Карточки, находящиеся в ротации
            if x.state.period > 0:
                AppendCards(cards_in_rotations, x.card, x.card_id)

            #Карточки, которые уже были в ротации, но имеют статус "новое"(используется при сбросе прогресса по словарю)
            if x.state.period == 0:
                AppendCards(new_cards, x.card, x.card_id)

    #Добавление, преобразованных в json-формат, новых карточек
    for y in all_new_cards:
        card_translations = y.translation.all()
        active_collection_id = collection_user.active_collection_id
        if y.collection_id == active_collection_id:
            AppendCards(new_cards, y, y.pk)

    response = (cards_in_rotations+new_cards)[:count]

    if len(response) == 0:
        return 'Даже новых слов нету!'
    else: 
        return response
    
@router.post("/cards/study", auth=AuthBearer(), response={200: Success})
def accepts_response_of_user(request, payload: Actions):
    id_user = request.auth

    def UpdateState(state):
        setattr(Table_for_update, 'state_id', state)
        Table_for_update.save()

    def UpdatePenaltyStep(flag):
        setattr(Table_for_update, 'penalty_step', flag)
        Table_for_update.save()

    def UpdatePenaltyStateId(meaning):
        setattr(Table_for_update, 'penalty_state_id', meaning)
        Table_for_update.save() 
    
    def CreatedNewCards(state):
        CardUserProgress.objects.create(
            user_id = id_user,
            card_id = user.id_card,
            state_id = state,
            time_created = 0,
            penalty_step = False,
            penalty_state_id = 0
        )    

    for user in payload.actions:
        progress = CardUserProgress.objects.filter(card_id = user.id_card, user_id = id_user)
        if progress != []:

            #Основная логика обработки карточек, находящихся в ротации
            for i in progress:
                Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)

                #Новое слово было известно
                if user.action == ActionsID.KNOWN_WORD.value and i.state_id == StatesID.NEW_WORD.value and i.penalty_step == False:
                    UpdateState(StatesID.WORD_IS_ALREADY_KNOWS.value)
                    return 200, {'status': 'Great'}
                
                #Новое слово не было известно
                if user.action == ActionsID.UNKNOWN_WORD.value and i.state_id == StatesID.NEW_WORD.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    return 200, {'status': 'Great'}


                if user.action == ActionsID.KNOWN_WORD.value and i.state_id >= StatesID.NEW_WORD.value and i.penalty_step == False:
                    for NewState in StatesID:                                             
                        if i.state_id == NewState:
                            UpdateState(NewState+1)
                            return 200, {'status': 'Great'}

                        if i.state_id == StatesID.WORD_IS_LEARNED.value:
                            return 200, {'status': 'Great'}

                #Обработка штрафного шага
                if user.action == ActionsID.UNKNOWN_WORD.value and i.state_id >= StatesID.AFTER_1_DAY.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    UpdatePenaltyStep(True)
                    UpdatePenaltyStateId(i.state_id)
                    return '{status: ok}'

                if user.action == ActionsID.KNOWN_WORD.value and i.state_id == StatesID.AFTER_5_MINUTES and i.penalty_step == True:
                    UpdateState(StatesID.AFTER_1_HOUR.value)
                    return '{status: ok}'
                    
                if user.action == ActionsID.KNOWN_WORD.value and i.state_id == StatesID.AFTER_1_HOUR.value and i.penalty_step == True:
                    UpdateState(i.penalty_state_id+1)
                    UpdatePenaltyStateId(0)
                    UpdatePenaltyStep(False)
                    return '{status: ok}'

        if progress == []:
            if user.action == ActionsID.UNKNOWN_WORD:
                CreatedNewCards(StatesID.AFTER_5_MINUTES.value)
                return 'Карточка в ротации'

            if user.action == ActionsID.KNOWN_WORD:
                CreatedNewCards(StatesID.WORD_IS_ALREADY_KNOWS.value)
                return 'Карточку знали заранее'

@router.post("/card/remote_progress")
def remote_CardUserProgress(request, id_user: int):
    all = CardUserProgress.objects.filter(user_id = id_user)
    for i in all:
        Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
        setattr(Table_for_update, 'state_id', StatesID.NEW_WORD.value)
        setattr(Table_for_update, 'penalty_step', False)
        setattr(Table_for_update, 'penalty_state_id', 0)
        Table_for_update.save()
    return 'Прогресс сброшен'
    
@router.post("/card/choose_collection")
def choose_collection(request, name_collection: str, id_user: int):
    all = CardCollection.objects.filter(name = name_collection)
    for i in all:
        if name_collection == i.name:
            Table_for_update = get_object_or_404(User, id = id_user)
            setattr(Table_for_update, 'active_collection_id', i.id)
            Table_for_update.save() 
    return '{status: ok}'

@router.get("/card/progress_get")
def Доступ_вне_зависимости_от_статуса(request):
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
    return CardUserProgr_list

@router.get("/card/all", response=List[CardOut])
def Получить_все_карточки(request):
    card_list=[]
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

@router.post("/card/add")
def Создать_карточку(request, payload: CardCollectionIn, id_collection: int):
    for card in payload.cards:
        card_object = Card.objects.create(
            collection_id = id_collection,
            word = card.word,
            transcription = card.transcription,
            type = card.type
                )
        for translation in card.translation:
            Translation.objects.create(
                word = translation,
                card = card_object
                )
    return f'{card_object.word} с id = {card_object.id} Записано в базу данных!'

