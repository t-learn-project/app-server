from ninja import Router, Schema
from .models import Card, Collection, User, CardProgress, Rotation
from typing import List

router = Router()

class CardOut(Schema):
    id: int
    word: str
    translation: str


class CardIn(Schema):
    collection_id: int
    word: str
    translation: str

class CardsOut(Schema):
    count: int
    cards: List[CardOut]


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
    }