from ninja import NinjaAPI
from tlearn.api import router

api = NinjaAPI()

api.add_router("", router)

