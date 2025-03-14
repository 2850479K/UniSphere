from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
from .models import StudentPost, PostFile, StudentProfile, RecruiterProfile, User
from .forms import StudentPostForm, ProfileEdiForm, UserRegisterForm, RecruiterProfileForm, StudentSearchForm

def home(request):
    return render(request, 'UniSphereApp/home.html', {'user': request.user})

def post_list(request):
    posts = StudentPost.objects.all().order_by('-timestamp')
    return render(request, 'UniSphereApp/post_list.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Project posted successfully.")
            return redirect('UniSphereApp:post_list')
    else:
        form = StudentPostForm()
    return render(request, 'UniSphereApp/create_post.html', {'form': form})

@login_required
def view_post(request, project_id):
    post = get_object_or_404(StudentPost, id=project_id)
    if post.user != request.user:
        messages.error(request, "You are not authorised to edit this post.")
        return redirect('UniSphereApp:post_list')
    if request.method == 'POST':
        if 'delete' in request.POST:
            post.delete()
            messages.success(request, "Post successfully deleted")
            return redirect('UniSphereApp:post_list')
        form = StudentPostForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('files')
        if form.is_valid():
            form.save()
            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Post updated successfully.")
            return redirect('UniSphereApp:view_post', project_id=post.id)
    else:
        form = StudentPostForm(instance=post)
    return render(request, 'UniSphereApp/view_post.html', {'form': form, 'post': post})

@login_required
def edit_post(request, project_id):
    post = get_object_or_404(StudentPost, id=project_id)
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('UniSphereApp:view_post', project_id=project_id)
    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('files')
        if form.is_valid():
            form.save()
            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Post updated successfully.")
            return redirect('UniSphereApp:view_post', project_id=post.id)
    else:
        form = StudentPostForm(instance=post)
    return render(request, 'UniSphereApp/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, project_id):
    post = get_object_or_404(StudentPost, id=project_id)
    if post.user != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('UniSphereApp:view_post', project_id=project_id)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post successfully deleted.")
        return redirect('UniSphereApp:post_list')
    return redirect('UniSphereApp:view_post', project_id=project_id)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()
            return redirect('UniSphereApp:login')
    else:
        form = UserRegisterForm()
    return render(request, 'UniSphereApp/register.html', {'form': form})

def create_recruiter_profile(request):
    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('UniSphereApp:home')
    else:
        form = RecruiterProfileForm()
    return render(request, 'UniSphereApp/create_recruiter_profile.html', {'form': form})

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
    return render(request, 'UniSphereApp/search_students.html', {'form': form, 'students': students})

@login_required
def profile(request):
    if request.user.role == 'student':
        user_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    else:
        user_profile, created = RecruiterProfile.objects.get_or_create(user=request.user)
    return render(request, 'UniSphereApp/profile.html', {'user_profile': user_profile})

@login_required
def edit_profile(request):
    if request.user.role == 'student':
        profile_obj = get_object_or_404(StudentProfile, user=request.user)
        form_class = ProfileEdiForm
    else:
        profile_obj = get_object_or_404(RecruiterProfile, user=request.user)
        form_class = RecruiterProfileForm
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect('UniSphereApp:profile')
    else:
        form = form_class(instance=profile_obj)
    return render(request, 'UniSphereApp/edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return render(request, 'UniSphereApp/logout.html')
