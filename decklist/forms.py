from django import forms

from .models import Decklist, Cardlist, Combolist

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
        fields = ('title',)
        
class DecklistSimulatorForm(forms.ModelForm):
    
    class Meta:
        model = Decklist
        fields = ('runs', 'hand_size')
        
class CardlistEditForm(forms.ModelForm):
    
    class Meta:
        model = Cardlist
        fields = ('card_name', 'card_amount', 'card_classification')
        
class ComboEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        pid=kwargs.pop('pid', None)
        super().__init__(*args, **kwargs)
        self.fields['combo'].queryset = Cardlist.objects.filter(deck_list_id=pid)
        
    class Meta:
        model = Combolist
        fields = ('combo',)
        
class ComboCreateForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        pid=kwargs.pop('pid', None)
        super(ComboCreateForm, self).__init__(*args, **kwargs)
        self.fields['combo'] = forms.ModelMultipleChoiceField(required=False, queryset=Cardlist.objects.filter(deck_list_id=pid))
        
    class Meta:
        model = Combolist
        fields = ('combo',)