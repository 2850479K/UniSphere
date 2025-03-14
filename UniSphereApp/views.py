from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Project, StudentPost, PostFile, RecruiterProfile, StudentProfile
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, RecruiterProfileForm, StudentSearchForm, StudentProfileForm

User = get_user_model()

# Authentication

def home(request):
    return render(request, 'UniSphereApp/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'UniSphereApp/register.html', {'form': form})

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = StudentProfile.objects.get_or_create(user=profile_user)
    projects = Project.objects.filter(user=profile_user).order_by("-timestamp")[:5]

    is_owner = request.user == profile_user  # ✅ Ensure only the owner can edit

    if request.method == "POST" and is_owner:
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if form.cleaned_data.get("delete_picture"):  
                profile.delete_profile_picture()  # ✅ Delete profile picture if requested
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=profile_user.username)
    else:
        form = StudentProfileForm(instance=profile)

    return render(
        request, 
        "UniSphereApp/profile.html", 
        {"form": form, "profile": profile, "projects": projects, "profile_user": profile_user, "is_owner": is_owner}
    )

@login_required
def my_profile(request):
    """Redirects the user to their own profile page."""
    return redirect('profile', username=request.user.username)

# Portfolio & Projects

def user_portfolio(request, username):
    profile_user = get_object_or_404(User, username=username)
    projects = Project.objects.filter(user=profile_user).order_by('-timestamp')
    return render(request, 'UniSphereApp/portfolio.html', {'projects': projects, 'profile_user': profile_user})

def project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    posts = StudentPost.objects.filter(project=project).order_by('-timestamp')
    return render(request, 'UniSphereApp/project.html', {'project': project, 'posts': posts})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, "Project created successfully!")
            return redirect('project', project_id=project.id)

    else:
        form = ProjectForm()

    return render(request, 'UniSphereApp/create_project.html', {'form': form})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.user:
        messages.error(request, "You are not authorized to edit this project.")
        return redirect('project', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('project', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'UniSphereApp/edit_project.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.user:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('project', project_id=project.id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project successfully deleted.")
        return redirect('user_portfolio', username=request.user.username)

    return redirect('project', project_id=project.id)

# Posts

@login_required
def create_post(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.project = project
            post.save()

            for file in files:
                PostFile.objects.create(post=post, file=file)

            messages.success(request, "Post added successfully.")
            return redirect('project', project_id=project.id)

    else:
        form = StudentPostForm()

    return render(request, 'UniSphereApp/create_post.html', {'form': form, 'project': project})

@login_required
def view_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    return render(request, 'UniSphereApp/view_post.html', {'post': post})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)

    if request.user != post.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('project', project_id=post.project.id)

    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('files')

        if form.is_valid():
            post.save()

            files_to_delete = request.POST.getlist('delete_files')
            PostFile.objects.filter(id__in=files_to_delete).delete()

            for file in files:
                PostFile.objects.create(post=post, file=file)

            messages.success(request, "Post updated successfully.")
            return redirect('project', project_id=post.project.id)

    else:
        form = StudentPostForm(instance=post)
        existing_files = PostFile.objects.filter(post=post)

    return render(request, 'UniSphereApp/edit_post.html', {'form': form, 'post': post, 'existing_files': existing_files})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)

    if post.user != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('project', project_id=post.project.id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post successfully deleted.")
        return redirect('project', project_id=post.project.id)

    return redirect('project', project_id=post.project.id)

# Recruiter Profile & Student Search

@login_required
def create_recruiter_profile(request):
    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('home')
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
