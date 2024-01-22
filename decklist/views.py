from django.shortcuts import render, get_object_or_404, redirect
from .models import Decklist
from .forms import DecklistForm, DecklistFormEdit, DecklistSimulatorForm
from .functions import deck_importer, validate_json, create_card, simulation, combo_checker
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json

# Create your views here.
def post_decklist(request):
    # show decklists
    decklists = Decklist.objects.filter(author = request.user)
    if len(decklists) > 0:
        return render(request, 'decklist/post_decklist.html', {'decklists': decklists})
    else:
        # blank template
        return render(request, 'decklist/post_decklist_blank.html')

def homepage(request):
    if request.user.is_authenticated:
        return redirect('post_decklist')
    else:
        return render(request, 'decklist/homepage.html')

def decklist_detail(request, pk):
    # show ideal output of complete. take into account just made lists
    # create new dictionary?-list of dictionary
    decklist = get_object_or_404(Decklist, pk=pk)
    clean_dict = []
    for key, item in decklist.data.items():
        template_dict = {'Name': key, 'Copies': item[0], 'Engine': item[1], 'Categorization': item[2]}
        clean_dict.append(template_dict)

    return render(request, 'decklist/decklist_detail.html', {'decklist': decklist, 'clean_dict': clean_dict})


def register_page(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password=password)
            login(request, user)
            messages.success(request, ("registration succecssful"))
            return redirect('post_decklist')
        # else:
        #     form = UserCreationForm()
    return render(request, 'decklist/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        request.POST.get('username')
        request.POST.get('password')
    else:
        return render(request, 'decklist/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You were logged out"))
    return redirect('post_decklist')

def decklist_simulator(request):
    # maybe make function local to get card objects available?
    # create card item list while running sim
    # {'kashtira unicorn': [1, 'engine', 'starter']}
    # select decklist here, go to run page
    # maybe just incorporate it into the detail page, add a button to run page
    decklists = Decklist.objects.order_by('title')
    return render(request, 'decklist/decklist_simulator.html', {'decklists': decklists})

def decklist_simulator_run(request,pk):
    # actually runinng the sim-get number of runs, handsize
    decklist = get_object_or_404(Decklist, pk=pk)
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

def decklist_simulator_results(request, pk):
    decklist = get_object_or_404(Decklist, pk=pk)
    # run create card here, run analysis func
    card_obj_list = create_card(decklist.data)
    # [analysis, output]
    output_dict = simulation(card_obj_list, decklist.runs, decklist.hand_size, decklist.deck_combo)
    # print(output_dict)
    return render(request, 'decklist/decklist_simulator_result.html', {'output': output_dict[1], 'analysis': output_dict[0], 'runs': decklist.runs})

def decklist_new(request):
    if request.method == 'POST':
        # convert plaintext to dictionary, with default empty categories
        # brand new, default list
        form = DecklistForm(request.POST)
        if form.is_valid():
            decklist = form.save(commit=False)
            decklist.author = request.user
            json_out = deck_importer(decklist.deck_plaintext)
            if json_out != None:
                decklist.data = json_out
            else:
                # any way to show failure?
                return redirect('post_decklist')
            decklist.save()
            return redirect('decklist_detail', pk=decklist.pk)
    else:
        # different view for editing decklist
        form = DecklistForm()
    # this should be taking the plaintext format
    return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'New Decklist'})


def decklist_edit(request, pk):
    decklist = get_object_or_404(Decklist, pk=pk)
    if request.method == "POST":
        form = DecklistFormEdit(request.POST, instance=decklist)
        if form.is_valid():
            decklist = form.save(commit=False)
            decklist.author = request.user
            if validate_json(decklist.data):
                if combo_checker(decklist.deck_combo, decklist.data):
                    decklist.save()
        return redirect('decklist_detail', pk=decklist.pk)
    else:
        form = DecklistFormEdit(instance=decklist)
    return render(request, 'decklist/decklist_edit.html', {'form': form, 'layout': 'Edit Decklist'})

