from django.contrib import admin
from .models import Decklist, Cardlist, Combolist
# Register your models here.

admin.site.register(Combolist)
admin.site.register(Cardlist)
admin.site.register(Decklist)