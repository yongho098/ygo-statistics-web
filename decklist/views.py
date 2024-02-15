from django.shortcuts import render, get_object_or_404, redirect
from .models import Decklist, Cardlist, Combolist
from .forms import DecklistForm, DecklistFormEdit, DecklistSimulatorForm, CardlistEditForm, ComboEditForm, ComboCreateForm
from .functions import deck_importer, create_card, simulation, deck_importer_sample
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.

# shows all decklists
def post_decklist(request):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    # show decklists belonging to user
    decklists = Decklist.objects.filter(author = request.user)
    if len(decklists) > 0:
        return render(request, 'decklist/post_decklist.html', {'decklists': decklists})
    else:
        # blank template
        return render(request, 'decklist/post_decklist_blank.html')

#homepage-when logging in
def homepage(request):
    if request.user.is_authenticated:
        return redirect('post_decklist')
    else:
        return render(request, 'decklist/homepage.html')

#shows cards in decklist
def decklist_detail(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # show ideal output of complete. take into account just made lists
    decklist = get_object_or_404(Decklist, pk=pk)
    cards = Cardlist.objects.filter(deck_list_id=pk)
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    return render(request, 'decklist/decklist_detail.html', {'decklist': decklist, 'cards': cards})

# def logout2(request):
#     return redirect('homepage')

def logout_microsoft(request):
    #this should have a click to log out button for microsoft-go direct?
    logout(request)
    return render(request, 'decklist/logout_microsoft.html', {})

#doesnt exist?
def decklist_simulator(request):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    decklists = Decklist.objects.order_by('title')
    return render(request, 'decklist/decklist_simulator.html', {'decklists': decklists})

# variables for running simulator
def decklist_simulator_run(request,pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # actually runinng the sim-get number of runs, handsize
    decklist = get_object_or_404(Decklist, pk=pk)
    
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == "POST":
        form = DecklistSimulatorForm(request.POST, instance=decklist)
        if form.is_valid():
            decklist = form.save(commit=False)
            decklist.author = request.user
            decklist.save()
        return redirect('decklist_simulator_result', pk=decklist.pk)
    else:
        form = DecklistSimulatorForm(instance=decklist)
    return render(request, 'decklist/decklist_simulator_run.html', {'form': form, 'decklist': decklist})

# shows results
def decklist_simulator_results(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    decklist = get_object_or_404(Decklist, pk=pk)
    # run create card here, run analysis func
    cards = Cardlist.objects.filter(deck_list_id=pk)
    combos = Combolist.objects.filter(deck_list_id=pk)
    
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    # grabbing data from card db and converting into card objects
    temp_dict = {}
    for card in cards:
        temp_dict[card.card_name]=[card.card_amount, '', card.card_classification]
    
    card_obj_list = create_card(temp_dict)
    
    # refactor combos here
    temp_combo=[]
    for combo in combos:
        temp_append=[]
        for card in combo.combo.all():
            temp_append.append(card.card_name)
        temp_combo.append(temp_append)
    # print(temp_combo)
    
    # [analysis, output]
    output_dict = simulation(card_obj_list, decklist.runs, decklist.hand_size, temp_combo)
    return render(request, 'decklist/decklist_simulator_result.html', {'output': output_dict[1], 'analysis': output_dict[0], 'runs': decklist.runs})

# creates a new decklist
def decklist_new(request):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # have a sample decklist option?-function
    if request.method == 'POST':
        # convert plaintext to dictionary, with default empty categories
        # brand new, default list
        form = DecklistForm(request.POST)
        if form.is_valid():
            decklist = form.save(commit=False)
            decklist.author = request.user
            json_out = deck_importer(decklist.deck_plaintext)
            if json_out != None:
                messages.success(request, 'Decklist created successfully.')
                decklist.save()
                # new function to make decklist database entry
                for cardloop in json_out.items():
                    card_entry = Cardlist(deck_list_id = decklist.pk, card_name = cardloop[0], card_amount=cardloop[1][0])
                    card_entry.save()
            else:
                # any way to show failure?
                messages.error(request, 'Invalid decklist input.')
                return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'New Decklist'})
            return redirect('decklist_detail', pk=decklist.pk)
    else:
        # different view for editing decklist
        form = DecklistForm()
    # this should be taking the plaintext format
    return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'New Decklist'})

# give a sample decklist
def decklist_sample(request):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # issue by allowing users to create continuously
    if request.method == 'POST':
        # convert plaintext to dictionary, with default empty categories
        # brand new, default list
        form = DecklistForm()
        output=Decklist(title='Sample Decklist', author_id=request.user.id)
        json_out = deck_importer_sample()
        if json_out != None:
            
            messages.success(request, 'Decklist created successfully.')
            output.save()
            # new function to make decklist database entry
            for cardloop in json_out.items():
                card_entry = Cardlist(deck_list_id = output.pk, card_name = cardloop[0], card_amount=cardloop[1][0])
                card_entry.save()
        else:
            # any way to show failure?
            messages.error(request, 'Invalid decklist input.')
            return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'New Decklist'})
        return redirect('decklist_detail', pk=output.pk)
    else:
        form = DecklistForm()
        return render(request, 'decklist/decklist_sample.html', {'form': form, 'layout': 'New Decklist'})
    
# edit decklist setting (name)
def decklist_edit(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # create object list and update
    decklist = get_object_or_404(Decklist, pk=pk)
    
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == "POST":
        # submission
        form = DecklistFormEdit(request.POST, instance=decklist)
        if form.is_valid():
            decklist = form.save(commit=False)
            decklist.author = request.user
            decklist.save()  
            return redirect('decklist_detail', pk=decklist.pk)
    else:
        form = DecklistFormEdit(instance=decklist)        
        return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'Edit Decklist'})

# edit cards in deck
def card_edit(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    cards = get_object_or_404(Cardlist, pk=pk)
    # checking if user is author
    if not request.user == cards.deck_list.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == "POST":
        form = CardlistEditForm(request.POST, instance=cards)
        if form.is_valid():
            messages.success(request, 'Card updated successfully.')
            cardlist = form.save(commit=False)
            cardlist.save()
            return redirect('decklist_detail', pk=cardlist.deck_list_id)
    else:
        form = CardlistEditForm(instance=cards)
        return render(request, 'decklist/card_edit.html', {'form': form})

def card_new(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    decklist = get_object_or_404(Decklist, pk=pk)
    
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == "POST":
        form = CardlistEditForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Card added successfully.')
            cardlist = form.save(commit=False)
            cardlist.deck_list_id=pk
            cardlist.save()
            return redirect('decklist_detail', pk=cardlist.deck_list_id)
    else:
        form = CardlistEditForm()
        return render(request, 'decklist/card_edit.html', {'form': form})
    pass

# create a new combo
def combo_new(request,  pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    decklist = get_object_or_404(Decklist, pk=pk)
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    # posting new combo
    if request.method == "POST":
        form = ComboCreateForm(request.POST, pid=pk)
        if form.is_valid():
            picked=form.cleaned_data
            # print(picked['combo'].all().count())
            # checking wheter theres at least 2 cards - add a maximum check?
            if picked['combo'].all().count() <= 1:
                messages.error(request, 'Please select at least 2 cards.')
                return render(request, 'decklist/combo_edit.html', {'form': form})
            else:
                # initial combo has at least 2 cards
                messages.success(request, 'Combo added successfully.')
                combolist = form.save(commit=False)
                combolist.deck_list_id=pk
                user = combolist.save()
                form.save_m2m()
                return redirect('combo_detail', pk=pk)
    else:
        form=ComboCreateForm(pid=pk)
        return render(request, 'decklist/combo_edit.html', {'form': form})

# edit existing combos
def combo_edit(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    combo = get_object_or_404(Combolist, pk=pk)
    # checking if user is author
    if not request.user == combo.deck_list.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == "POST":
        form = ComboEditForm(request.POST, instance=combo, pid=combo.deck_list_id)
        if form.is_valid():
            picked=form.cleaned_data
            # print(picked['combo'].all().count())
            # checking wheter theres at least 2 cards - add a maximum check?
            if picked['combo'].all().count() <= 1:
                messages.error(request, 'Please select at least 2 cards.')
                return render(request, 'decklist/combo_edit.html', {'form': form})
            else:
                # has at least 2 cards for combo
                messages.success(request, 'Combo updated successfully.')
                form.save()
                return redirect('combo_detail', pk=combo.deck_list_id)
            
    else:
        form=ComboEditForm(instance=combo, pid=combo.deck_list_id)
        return render(request, 'decklist/combo_edit.html', {'form': form})

# show all combos for current deck
def combo_detail(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    # show ideal output of complete. take into account just made lists
    decklist = get_object_or_404(Decklist, pk=pk)
    combos = Combolist.objects.filter(deck_list_id=pk)
    
    # checking if user is author
    if not request.user == decklist.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    return render(request, 'decklist/combo_detail.html', {'combos': combos, 'pk': pk})

# delete selected deck
def delete_deck(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    #need separate for deleting combos, deck?
    deck=get_object_or_404(Decklist, pk=pk)
    
    # checking if user is author
    if not request.user == deck.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == 'POST':
        # deleting the decklist
        deck.delete()
        messages.success(request, 'Deck deleted successfully.')
        return redirect(post_decklist)
    return render(request, 'decklist/delete_deck.html', {'deck': deck})

# delete selected card and related combos
def delete_card(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    card=get_object_or_404(Cardlist, pk=pk)
    combos = Combolist.objects.filter(deck_list_id=card.deck_list_id)
    combos_to_delete=[]
    #print(combos_to_delete)
    
    # checking if user is author
    if not request.user == card.deck_list.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == 'POST':
        # deleting the card
        for combo in combos:
            for card2 in combo.combo.all():
                if card2==card:
                    # can do here since you can only have 1 version of a card in a combo
                    combos_to_delete.append(combo)
        for deleted_combo in combos_to_delete:
            deleted_combo.delete()
        # delete combo first then the card
        card.delete()
        messages.success(request, 'Card deleted successfully.')
        return redirect(decklist_detail, pk=card.deck_list_id)
    return render(request, 'decklist/delete_card.html', {'card': card})

# delete selected combo
def delete_combo(request, pk):
    # redirect to homepage if user is not logged in
    if not request.user.is_authenticated:
        return redirect('homepage')
    
    combo = get_object_or_404(Combolist, pk=pk)
    
    # checking if user is author
    if not request.user == combo.deck_list.author:
        response = HttpResponse()
        response.status_code = 403
        return response
    
    if request.method == 'POST':
        # deleting the card
        combo.delete()
        messages.success(request, 'Combo deleted successfully.')
        return redirect('combo_detail', pk=combo.deck_list_id)
    return render(request, 'decklist/delete_combo.html', {'combo': combo})

