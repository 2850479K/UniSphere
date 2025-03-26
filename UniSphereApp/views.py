from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from .models import Project, StudentPost, PostFile, RecruiterProfile, StudentProfile, Comment, Like, Share, FriendRequest, SharedPost
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, RecruiterProfileForm, StudentSearchForm, StudentProfileForm, CreateProfileForm, EditProfileForm
from django.http import JsonResponse


User = get_user_model()

# Authentication
def home(request):
    return render(request, 'UniSphereApp/home.html')

def welcomepage(request):
    return render(request, 'UniSphereApp/welcomepage.html')

def about(request):
    return render(request, 'UniSphereApp/about.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])  
            if user is not None:
                login(request, user)  
                return redirect('create_profile')
    else:
        form = UserRegisterForm()

    return render(request, 'UniSphereApp/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
                return JsonResponse({"message": "Login successful!", "redirect": "my_profile"}, status=200)
            messages.success(request, "You have successfully logged in.")
            return redirect('my_profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
                return JsonResponse({"error": "Invalid username or password."}, status=400)
            messages.error(request, "Invalid username or password.")

    return render(request, 'UniSphereApp/login.html')

@login_required
def create_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CreateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile created successfully!")
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, "Error creating profile. Please check the form.")
    else:
        form = CreateProfileForm(instance=profile)

    return render(request, 'UniSphereApp/create_profile.html', {'form': form})

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = StudentProfile.objects.get_or_create(user=profile_user)
    projects = Project.objects.filter(user=profile_user).order_by("-timestamp")[:5] 

    is_owner = request.user == profile_user  
    is_friend = profile.friends.filter(user=request.user).exists() 

    friend_request_sent = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user, status='pending').exists()
    friend_request_received = FriendRequest.objects.filter(from_user=profile_user, to_user=request.user, status='pending').exists()

    if profile.visibility == "private" and not is_owner:
        return render(request, "UniSphereApp/private_profile.html", {"profile": profile})

    return render(
        request, 
        "UniSphereApp/profile.html", 
        {
            "profile": profile, 
            "projects": projects,  
            "profile_user": profile_user, 
            "is_owner": is_owner,
            "is_friend": is_friend,
            "friend_request_sent": friend_request_sent,
            "friend_request_received": friend_request_received,
        }
    )

@login_required
def my_profile(request):
    return redirect('profile', username=request.user.username)

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

@login_required
def edit_profile(request):
    profile = get_object_or_404(StudentProfile, user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if request.POST.get("delete_picture"):  
                profile.profile_picture.delete()  
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'UniSphereApp/edit_profile.html', {'form': form})

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
            messages.error(request, "Error creating project. Please check the form.")

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
            messages.success(request, "Project updated successfully!")
            return redirect('project', project_id=project.id)
        else:
            messages.error(request, "Error updating project. Please check the form.")

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
        messages.success(request, "Project deleted successfully!")
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

            messages.success(request, "Post added successfully!")
            return redirect('project', project_id=project.id)
        else:
            messages.error(request, "Error adding post. Please check the form.")

    else:
        form = StudentPostForm()

    return render(request, 'UniSphereApp/create_post.html', {'form': form, 'project': project})


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

            messages.success(request, "Post updated successfully!")
            return redirect('project', project_id=post.project.id)
        else:
            messages.error(request, "Error updating post. Please check the form.")

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
        messages.success(request, "Post deleted successfully!")
        return redirect('project', project_id=post.project.id)

    return redirect('project', project_id=post.project.id)

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

# Social Features
@login_required
def get_comments(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    comments = post.comments.order_by('-created_at')[:5]  
    comments_data = [
        {"username": c.user.username, "content": c.content, "created_at": c.created_at.strftime('%Y-%m-%d %H:%M')}
        for c in comments
    ]
    return JsonResponse({"comments": comments_data})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)

    existing_like = Like.objects.filter(user=request.user, post=post)
    if existing_like.exists():
        existing_like.delete()
    else:
        Like.objects.create(user=request.user, post=post)

    return redirect('project', project_id=post.project.id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)

    return redirect('project', project_id=post.project.id)

@login_required
def view_all_comments(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    return render(request, 'UniSphereApp/all_comments.html', {'post': post, 'comments': comments})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user, status=FriendRequest.PENDING)
        if not created:
            return JsonResponse({"message": "Friend request already sent."})
    return JsonResponse({"message": "Friend request sent"})

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, status=FriendRequest.PENDING)
    friend_request.status = FriendRequest.ACCEPTED
    friend_request.save()

    friend_request.from_user.studentprofile.friends.add(friend_request.to_user.studentprofile)
    friend_request.to_user.studentprofile.friends.add(friend_request.from_user.studentprofile)

    return redirect('profile', username=request.user.username)

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('profile', username=request.user.username)

@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.PENDING)
    return render(request, 'UniSphereApp/friend_requests.html', {'requests': requests})

@login_required
def share_post(request, post_id):
    original_post = get_object_or_404(StudentPost, id=post_id)

    if SharedPost.objects.filter(user=request.user, original_post=original_post).exists():
        messages.warning(request, "You have already shared this post.")
    else:
        SharedPost.objects.create(user=request.user, original_post=original_post)
        messages.success(request, "Post shared successfully!")

    return redirect('shared_posts_list')

@login_required
def shared_posts_list(request):
    shared_posts = SharedPost.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'UniSphereApp/shared_posts.html', {'shared_posts': shared_posts})
