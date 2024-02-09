from django.db import models
from django.conf import settings
# Create your models here.

category_choice = (
    ('Starter', 'Starter'),
    ('Garnet', 'Garnet'),
)
card_amounts = (
    (1, 1),
    (2, 2), 
    (3, 3),
)

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
    # deck_combo = models.JSONField(default=[[]])
    # data = models.JSONField(default=dict)
    runs = models.PositiveSmallIntegerField(default=100)
    hand_size = models.PositiveSmallIntegerField(default=5)
    
    def __str__(self):
        return self.title
    
class Cardlist(models.Model):
    # individual cards
    deck_list = models.ForeignKey(Decklist, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=200)
    card_amount = models.PositiveSmallIntegerField(choices=card_amounts)
    card_classification = models.CharField(max_length=50, blank=True, choices=category_choice)

    
    def __str__(self):
        return self.card_name

class Combolist(models.Model):
    # combo list for decklists
    deck_list = models.ForeignKey(Decklist, on_delete=models.CASCADE)
    combo = models.ManyToManyField(Cardlist)
    
    def __str__(self):
        return self.deck_list.title

    