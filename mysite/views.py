import os
import json

from django.conf import settings
from django.shortcuts import redirect, render
import requests
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpRequest


__version__ = "0.2.0"

    
@settings.AUTH.login_required
def index(request):
    # only need 1 form of login gate?
    user = settings.AUTH.get_user(request)
    assert user  # User would not be None since we decorated this view with @login_required
    user_exist = User.objects.filter(username=user['preferred_username']).exists()
    if user_exist:
        # should be unique emails
        userobject = User.objects.filter(username=user['preferred_username'])[0]
        login(request, userobject)
    else:
        #create user
        django_user = User.objects.create_user(username=user['preferred_username'])
        login(request, django_user)
    
    return redirect('post_decklist')


# Instead of using the login_required decorator,
# here we demonstrate how to handle the error explicitly.
def call_downstream_api(request):
    token = settings.AUTH.get_token_for_user(request, os.getenv("SCOPE", "").split())
    if "error" in token:
        return redirect(settings.AUTH.login)
    api_result = requests.get(  # Use access token to call downstream api
        os.getenv("ENDPOINT"),
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()  # Here we assume the response format is json
    return render(request, 'display.html', {
        "title": "Result of downstream API call",
        "content": json.dumps(api_result, indent=4),
    })

