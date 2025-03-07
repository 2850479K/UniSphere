from django.shortcuts import render, redirect
from .models import RecruiterProfile
from .forms import RecruiterProfileForm
from django.db.models import Q
from .models import StudentProfile
from .forms import StudentSearchForm

# Create your views here.
def create_recruiter_profile(request):
    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('recruiter_dashboard')
    else:
        form = RecruiterProfileForm()
    return render(request, 'recruiter/create_profile.html', {'form': form})

def search_students(request):
    form = StudentSearchForm(request.GET)
    students = StudentProfile.objects.all()

    if form.is_valid():
        if form.cleaned_data.get('name'):
            students = students.filter(user__username__icontains=form.cleaned_data['name'])
        if form.cleaned_data.get('school'):
            students = students.filter(school__icontains=form.cleaned_data['school'])
        if form.cleaned_data.get('course'):
            students = students.filter(course__icontains=form.cleaned_data['course'])
        if form.cleaned_data.get('interests'):
            students = students.filter(interests__icontains=form.cleaned_data['interests'])
        if form.cleaned_data.get('skills'):
            students = students.filter(skills__icontains=form.cleaned_data['skills'])

    return render(request, 'recruiter/search_students.html', {'form': form, 'students': students})