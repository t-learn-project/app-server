from ninja import Router, Schema
from typing import List
import jwt
from ninja.security import HttpBearer
from django_enumfield import enum
from datetime import *
from core.settings import TLEARN_JWT_ACCESS_SECRET


class CardOut(Schema):
    id: int
    collection: str
    word: str
    transcription: str
    translation: List[str]
    type: int

class Success(Schema): 
    status: str

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        key = TLEARN_JWT_ACCESS_SECRET
        return jwt.decode(token, key, algorithms="HS256")["id"]

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
    UNKNOWN_WORD = 0,
    KNOWN_WORD = 1

class ResponseOfUser(Schema):
    action: int 
    card_id: int

class Actions(Schema):
    actions: List[ResponseOfUser]

class Collection(Schema): 
    name: str

class TranslationSetOut(Schema):
    id: int 
    word: str

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
    cards: List[CardIn]   

class CardCollectionCreate(Schema):
    name: str

class CreateUser(Schema):
    email: str
    first_name: str
    last_name: str
    active_collection_id: int