from django.db import models
from django.conf import settings
# Create your models here.

class Card:
    # all card shared properties. currently none. need to get this implemented first
    
    def __init__(self, name):
        # specific card
        self.name = name
        self.copy = 1
        # number in deck, default 1
        self.amount = 1
        # Either engine or non-engine since calcluating playability
        self.card_type = ''
        # applying Patrick Hoban's card type theory-turn into list since possible to have multiple
        # Starter, extender, defensive, offensive, garnet, consistency
        self.subtype = ''

class Decklist(models.Model):
    # toss in card classes here?
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    deck_plaintext = models.TextField()
    deck_combo = models.JSONField(default=[[]])
    data = models.JSONField(default=dict)
    runs = models.PositiveSmallIntegerField(default=100)
    hand_size = models.PositiveSmallIntegerField(default=5)
    
    
    def __str__(self):
        return self.title
    
