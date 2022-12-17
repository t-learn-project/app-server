from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from .models import *
from typing import List
from datetime import *
import datetime as datka
from ninja.security import django_auth
from .models_for_api import *

router = Router()

@router.get("/cards/study", auth=AuthBearer())
def returns_cards_for_study(request, count: int):
    id_user = request.auth
    progress = CardUserProgress.objects.filter(user_id = id_user)
    def AppendCards(list, arg, id, id_state):
        list.append({
                'id': id,
                'collection': arg.collection.name,
                'word': arg.word,
                'transcription': arg.transcription,
                'translation': [i.word for i in card_translations],
                'type': arg.type,
                'state_id': id_state
                })

    collection_user = User.objects.get(id = id_user)
    all_new_cards = Card.objects.filter(collection_id = collection_user.active_collection_id).exclude(id__in = CardUserProgress.objects.values_list('id'))#Карточки, которых нету в ротации
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
                AppendCards(cards_in_rotations, x.card, x.card_id, x.state.pk)

            #Карточки, которые уже были в ротации, но имеют статус "новое"(используется при сбросе прогресса по словарю)
            if x.state.period == 0:
                AppendCards(new_cards, x.card, x.card_id, 0)

    #Преобразование карточек в json-формат
    for y in all_new_cards[:count]:
        card_translations = y.translation.all()
        active_collection_id = collection_user.active_collection_id
        if y.collection.pk == active_collection_id:
            AppendCards(new_cards, y, y.pk, 0)
            

    response = (cards_in_rotations+new_cards)[:count]

    if len(response) == 0:
        return 'Have not new words'
    else: 
        return new_cards
    
@router.post("/cards/study", auth=AuthBearer())
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
            card_id = x.card_id,
            state_id = state,
            time_created = 0,
            penalty_step = False,
            penalty_state_id = 0
        )  
    for x in payload.actions:
        progress = CardUserProgress.objects.filter(card_id = x.card_id, user_id = id_user)
        if list(progress) != []:

            #Основная логика обработки карточек, находящихся в ротации
            for i in progress:
                Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)

                #Новое слово было известно
                if i.state_id == StatesID.NEW_WORD.value and x.action == ActionsID.KNOWN_WORD.value and i.penalty_step == False:
                    UpdateState(StatesID.WORD_IS_ALREADY_KNOWS.value)
                    #return 200, {'status': 'ok'}
                    
                #Новое слово не было известно
                if x.action == ActionsID.UNKNOWN_WORD.value and i.state_id == StatesID.NEW_WORD.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    #return 200, {'status': 'ok'}


                if i.state_id > StatesID.NEW_WORD.value and x.action == ActionsID.KNOWN_WORD.value and i.penalty_step == False:
                    for NewState in StatesID:   
                        if i.state_id == NewState and i.state_id != StatesID.WORD_IS_ALREADY_KNOWS and i.state_id != StatesID.WORD_IS_LEARNED.value:
                            UpdateState(NewState+1)
                            #return 200, {'status': 'ok'}
                            
                #Обработка штрафного шага
                if x.action == ActionsID.UNKNOWN_WORD.value and i.state_id >= StatesID.AFTER_1_DAY.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    UpdatePenaltyStep(True)
                    UpdatePenaltyStateId(i.state_id)
                    #return 200, {'status': 'ok'}

                if x.action == ActionsID.KNOWN_WORD.value and i.state_id == StatesID.AFTER_5_MINUTES and i.penalty_step == True:
                    UpdateState(StatesID.AFTER_1_HOUR.value)
                    #return 200, {'status': 'ok'}
                        
                if x.action == ActionsID.KNOWN_WORD.value and i.state_id == StatesID.AFTER_1_HOUR.value and i.penalty_step == True:
                    UpdateState(i.penalty_state_id+1)
                    UpdatePenaltyStateId(0)
                    UpdatePenaltyStep(False)
                    #return 200, {'status': 'ok'}
                
        if list(progress) == []:
            if x.action == ActionsID.UNKNOWN_WORD:
                CreatedNewCards(StatesID.AFTER_5_MINUTES.value)
                #return 200, {'status':'ok'}

            if x.action == ActionsID.KNOWN_WORD:
                CreatedNewCards(StatesID.WORD_IS_ALREADY_KNOWS.value)
                #return 200, {'status':'ok'} 
    return 200, {'status':'ok'} 
    
            
@router.post("/progress/", auth=AuthBearer(), response={200: Success})
def reset_progress(request):
    id_user = request.auth
    collection_user = User.objects.get(id = id_user)
    all = CardUserProgress.objects.filter(user_id = id_user)
    for i in all:
        Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
        if i.card.collection.pk == collection_user.active_collection_id:
            setattr(Table_for_update, 'state_id', StatesID.NEW_WORD.value)
            setattr(Table_for_update, 'penalty_step', False)
            setattr(Table_for_update, 'penalty_state_id', 0)
            Table_for_update.save()
    return 200, {'status': 'ok'}
    
@router.post("/collection/", auth=AuthBearer(), response={200: Success})
def set_active_collection(request, id_collection: int):
    id_user = request.auth
    all = CardCollection.objects.filter(pk = id_collection)
    for i in all:
        Table_for_update = get_object_or_404(User, id = id_user)
        setattr(Table_for_update, 'active_collection_id', i.id)
        Table_for_update.save() 
    return 200, {'status': 'ok'}

@router.get("/collections/", auth=AuthBearer())
def get_all_collections(request):
    collections = CardCollection.objects.all()
    response = []
    for x in collections:
        response.append({
            "id": x.pk,
            "name": x.name,
            "all_words": [i.word for i in Card.objects.filter(collection_id = x.pk)]
        }) 
    return response
    

@router.get("/active_collections/", auth=AuthBearer())
def get_active_collections(request):
    id_user = request.auth
    collection_id = User.objects.filter(id = id_user).values_list('active_collection_id', flat=True)
    return list(collection_id)

""" @router.post("/card/add")
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
    return f'{card_object.word} с id = {card_object.id} Записано в базу данных!' """
"""
@router.post("/collection/add")
def create_collection(request, payload: CardCollectionCreate):
    collection_object = CardCollection.objects.create(name = payload.name)
    return 'Success'

@router.post("/user/add")
def create_user(request, payload: CreateUser):
    user_object = User.objects.create(
        email = payload.email,
        first_name = payload.first_name,
        last_name = payload.last_name,
        active_collection_id = payload.active_collection_id
    )
    return f'{user_object}' """

