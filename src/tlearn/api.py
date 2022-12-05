from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from .models import *
from typing import List
from datetime import *
import datetime as datka
from operator import itemgetter

router = Router()

@router.get("/card/study")
def Returns_cards_for_study(request, count: int, id_user: int):
    progress = CardUserProgress.objects.filter(user_id = id_user)[:count]
    now_data = datka.datetime.now()
    new_cards = []
    cards_in_rotations = []
    def AppendCards(list, arg, id):
        list.append({
                'id': id,
                'collection': arg.collection.name,
                'word': arg.word,
                'transcription': arg.transcription,
                'translation': [i.word for i in card_translations],
                'type': arg.type
                }) 

    cards_in_progress_id = []
    collection_user = User.objects.filter(id = id_user)
    for l in collection_user:
        all_cards = Card.objects.filter(collection_id = l.active_collection_id)

    all_cards_id = []
    for i in all_cards:
        all_cards_id.append(i.id)

    for x in progress:
        cards_in_progress_id.append(x.card_id)
        active_collection_id = x.user.active_collection_id
        card_translations = x.card.translation.all()
        total = (now_data - x.time_created).seconds

        if x.state.period>=0 and total > x.state.period and x.card.collection.id == active_collection_id:
            if x.state.period > 0:
                AppendCards(cards_in_rotations, x.card, x.card_id)
            if x.state.period == 0:
                AppendCards(new_cards, x.card, x.card_id)
    
    new_cards_id = []
    for id in all_cards_id:
        if id not in cards_in_progress_id:
            new_cards_id.append(id)

    for id in new_cards_id:
        card = Card.objects.filter(id=id)
        for k in card:
            card_translations = k.translation.all()
            collection_user = User.objects.filter(id = id_user)
            for l in collection_user:
                if l.active_collection_id == k.collection_id:
                    new_cards.append({
                            'id': id,
                            'collection': k.collection.name,
                            'word': k.word,
                            'transcription': k.transcription,
                            'translation': [i.word for i in card_translations],
                            'type': k.type
                    })
            
    response = (cards_in_rotations+new_cards)[:count]
    
    if len(response) == 0:
        return 'Даже новых слов нету!'
    else:
        return response 
        
class StatesID(enum.Enum):
    NEW_WORD = 1,        
    AFTER_5_MINUTES = 2,     
    AFTER_1_HOUR = 3, 
    AFTER_1_DAY = 4, 
    AFTER_1_WEEK = 5, 
    AFTER_1_MOUNTH = 6, 
    AFTER_3_MOUNTH = 7, 
    WORD_IS_LEARNED = 8, 
    WORD_IS_ALREADY_KNOWS = 9

class ActionsID(enum.Enum):
    I_DONE_NOT_KNOW_THIS_WORD = 0,
    I_KNOW_THIS_WORD = 1

class ResponseOfUser(Schema):
    action: int 
    id_card: int

class Actions(Schema):
    actions: List[ResponseOfUser]

@router.post("/cards/study")
def Accepts_response_of_user(request, id_user: int, payload: Actions):
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
        if f'{progress}' != "<QuerySet []>":
            for i in progress:
                Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
                if user.action == ActionsID.I_KNOW_THIS_WORD.value and i.state_id == StatesID.NEW_WORD.value and i.penalty_step == False:
                    UpdateState(StatesID.WORD_IS_ALREADY_KNOWS.value)
                    return 'Слово было знакомо'

                if user.action == ActionsID.I_DONE_NOT_KNOW_THIS_WORD.value and i.state_id == StatesID.NEW_WORD.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    return 'Слово в ротации'

                if user.action == ActionsID.I_KNOW_THIS_WORD.value and i.state_id >= StatesID.NEW_WORD.value and i.penalty_step == False:
                    for NewState in StatesID:                                             
                        if i.state_id == NewState:
                            UpdateState(NewState+1)
                            return f'Слово покажется через {NewState+1}'

                        if i.state_id == StatesID.WORD_IS_LEARNED.value:
                            return 'Word is learned'

                #Обработка штрафного шага
                if user.action == ActionsID.I_DONE_NOT_KNOW_THIS_WORD.value and i.state_id >= StatesID.AFTER_1_DAY.value:
                    UpdateState(StatesID.AFTER_5_MINUTES.value)
                    UpdatePenaltyStep(True)
                    UpdatePenaltyStateId(i.state_id)
                    return '{status: ok}'

                if user.action == ActionsID.I_KNOW_THIS_WORD.value and i.state_id == StatesID.AFTER_5_MINUTES and i.penalty_step == True:
                    UpdateState(StatesID.AFTER_1_HOUR.value)
                    return '{status: ok}'
                    
                if user.action == ActionsID.I_KNOW_THIS_WORD.value and i.state_id == StatesID.AFTER_1_HOUR.value and i.penalty_step == True:
                    UpdateState(i.penalty_state_id+1)
                    UpdatePenaltyStateId(0)
                    UpdatePenaltyStep(False)
                    return '{status: ok}'


        if f'{progress}' == "<QuerySet []>":
            if user.action == ActionsID.I_DONE_NOT_KNOW_THIS_WORD:
                CreatedNewCards(StatesID.AFTER_5_MINUTES.value)
                return 'Карточка в ротации'

            if user.action == ActionsID.I_KNOW_THIS_WORD:
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

@router.post("/card/add")
def Создать_карточку(request, payload: CardCollectionIn, id_user: int, id_collection: int):
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
