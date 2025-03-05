from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # Log in user after registration
            return redirect('home')  # Redirect to homepage
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            return HttpResponse("Invalid login details")
    return render(request, 'login.html')

@login_required
def restricted_view(request):
    return HttpResponse("This is a restricted page. Only logged-in users can see this.")

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')  # Make sure 'dashboard.html' exists

def home(request):
    return render(request, 'home.html')  # Make sure 'home.html' exists
