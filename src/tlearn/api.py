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
    Progress = CardUserProgress.objects.filter(user_id = id_user)[:count]
    NowData = datka.datetime.now()
    NewCards = []
    CardsInRotation = []
    def AppendCards(list):
        list.append({
                'collection': x.card.collection.name,
                'word': x.card.word,
                'transcription': x.card.transcription,
                'translation': [i.word for i in card_translations],
                'type': x.card.type,
                'status': x.state.period})

    for x in Progress:
        collection_user = x.user.active_collection_id
        card_translations = x.card.translation.all()
        total = (NowData - x.time_created).seconds
        if x.state.period>=0 and total > x.state.period and x.card.collection.id == collection_user:
            if x.state.period == 0: 
                AppendCards(NewCards)
            if x.state.period>0:
                AppendCards(CardsInRotation)
    response =  (sorted(CardsInRotation, key=itemgetter('status'))+NewCards)[:count] 
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

@router.post("/cards/study")
def Accepts_response_of_user(request, action: int, id_card: int, id_user: int):
    Progress = CardUserProgress.objects.filter(card_id = id_card, user_id=id_user)
    Penalty_step = 0
    def UpdateState(state):
            setattr(Table_for_update, 'state_id', state)
            Table_for_update.save()

    for i in Progress:
        Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)    
        if action == 1 and i.state_id == StatesID.NEW_WORD.value and i.penalty_step == False:
            UpdateState(StatesID.WORD_IS_ALREADY_KNOWS.value)
            
        if action == 0 and i.state_id == StatesID.NEW_WORD.value:
            UpdateState(StatesID.AFTER_5_MINUTES.value)
            
        if action == 1 and i.state_id >= StatesID.NEW_WORD.value and i.penalty_step == False:
            for NewState in StatesID:                                             
                if i.state_id == NewState:
                    UpdateState(NewState+1)
                if i.state_id == StatesID.WORD_IS_LEARNED.value:
                    return 'Word is learned' 
                    
                      

""" #Штрафной шаг
        if i.state_id>1:
            for j in range(1,8):
                if i.state_id==j:
                    if i.state_id >= 3 and i.state_id != check_step:
                        check_step = j
                        Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
                        setattr(Table_for_update, 'state_id', 2)
                        setattr(Table_for_update, 'penalty_step', True)
                        Table_for_update.save()
                        append_progress(response)

                    if i.penalty_step == True and action==1:

                        if i.state_id == 2 and i.state_id != check_step:
                            Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
                            setattr(Table_for_update, 'state_id', 3)
                            Table_for_update.save()
                            append_progress(response)

                        if i.state_id == 3 and i.state_id == check_step and i.penalty_step == True:
                            Table_for_update = get_object_or_404(CardUserProgress, pk=i.id)
                            setattr(Table_for_update, 'state_id', check_step+1)
                            setattr(Table_for_update, 'penalty_step', False)
                            Table_for_update.save()
                            append_progress(response)
                        
                                                    
        if i.state_id == 8:
                break  
    return response """


@router.post("/card/choose_collection")
def choose_collection(request, name_collection: str, id_user: int):
    all = CardCollection.objects.all()
    for i in all:
        if name_collection == i.name:
            Table_for_update = get_object_or_404(User, pk = id_user)
            setattr(Table_for_update, 'active_collection_id', i.id)
            Table_for_update.save() 
    return 'Успешно'


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
    stata: List[Statistics] 

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
        id_state = 1
        CardUserProgress.objects.create(
                user_id = id_user,
                card_id = card_object.id,
                state_id = id_state,
                time_created = 0,
                penalty_step = False,
            ) 
    return f'{card_object.word} с id = {card_object.id} Записано в базу данных!'
