from django import forms

from .models import Decklist

# separate for new/editing
class DecklistForm(forms.ModelForm):

    class Meta:
        model = Decklist
        #fields to enter
        fields = ('title', 'deck_plaintext',)
        labels = {'deck_plaintext': 'Decklist'}
        
class DecklistFormEdit(forms.ModelForm):
    
    class Meta:
        model = Decklist
        fields = ('title', 'data', 'deck_combo')
        
class DecklistSimulatorForm(forms.ModelForm):
    
    class Meta:
        model = Decklist
        fields = ('runs', 'hand_size')