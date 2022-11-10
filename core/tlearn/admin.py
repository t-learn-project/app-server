from django.contrib import admin
from .models import *

admin.site.register(CardCollection)
admin.site.register(CardProgressStep)
admin.site.register(User)
admin.site.register(Card)
admin.site.register(CardUserProgress)
admin.site.register(CardState)
admin.site.register(Translation)