from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
import re
from django.shortcuts import render
from requests.auth import HTTPBasicAuth
import requests
from django.http import JsonResponse
# from .myapp import views


def signup_view(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('un')
        password = request.POST.get('pw')
        password_confirm = request.POST.get('pw')


        if not username:
            messages.error(request, 'Username is required')
            return redirect('signup_url')

        if len(username) > 150:
            messages.error(request, 'Username cannot be more than 150 characters')
            return redirect('signup_url')

        if not re.match(r'^[\w.@+-]+$', username):
            messages.error(request, 'Username can only contain letters, digits, and @/./+/-/_')
            return redirect('signup_url')


        if not password:
            messages.error(request, 'Password is required')
            return redirect('signup_url')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return redirect('signup_url')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('signup_url')


        if password.lower() in username.lower():
            messages.error(request, 'Password is too similar to username')
            return redirect('signup_url')

        common_passwords = ['password123',  'dragonball']
        if password.lower() in common_passwords:
            messages.error(request, 'Password is too common')
            return redirect('signup_url')

        # Create user
        user = User.objects.create_user(username, password=password)
        user.save()

        return redirect('login_url')

    template_name = 'auth_app/signup.html'
    return render(request, template_name)


def login_view(request):
    # Get all items API
    GET_URL = "https://edrx-dev1.fa.us2.oraclecloud.com/fscmRestApi/resources/11.13.18.05/itemsV2"
    AUTH = HTTPBasicAuth('CSP_COMMON_USER1', 'CSP@Jul240704')

    get_params = {
        'q': 'OrganizationCode=MFG01'
    }

    try:
        response = requests.get(GET_URL, params=get_params, auth=AUTH)
        response.raise_for_status()
        get_data = response.json()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

    if request.method == 'POST':
        un = request.POST.get('un')
        pw = request.POST.get('pw')
        user = authenticate(username=un, password=pw)
        if user:
            login(request, user)
            request.session['get_data'] = get_data  # Store data in the session
            return redirect('home')
        else:
            error_message = "Incorrect username or password. Please try again."
            return render(request, 'auth_app/login_page.html', {'error_message': error_message, 'get_data': get_data})

    return render(request, 'auth_app/login_page.html', {'get_data': get_data})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('signup_url')
    template_name = 'auth_app/logout.html'
    context = {}
    return render(request, template_name, context)


def dashboard_view(request):
    return render(request, 'auth_app/dashboard.html')
