from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from django.http import JsonResponse
from .models import Project, StudentPost, PostFile, RecruiterProfile, StudentProfile, Comment, Like, Share, FriendRequest, SharedPost
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, RecruiterProfileForm, StudentSearchForm, StudentProfileForm, CreateProfileForm, EditProfileForm

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
            messages.success(request, "You have successfully logged in.")
            return redirect('my_profile')
        else:
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
    
    if profile.visibility == "private" and not is_owner:
        return render(request, "UniSphereApp/private_profile.html", {"profile": profile})
    
    if request.method == "POST" and is_owner:
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if request.POST.get("delete_picture"):
                profile.delete_profile_picture()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=profile_user.username)
    else:
        form = StudentProfileForm(instance=profile)

    return render(
        request, 
        "UniSphereApp/profile.html", 
        {
            "form": form, 
            "profile": profile, 
            "projects": projects,  
            "profile_user": profile_user, 
            "is_owner": is_owner,
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
def add_comment(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('view_post', post_id=post.id)

@login_required
def get_comments(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    comments = list(post.comments.values('user__username', 'content', 'created_at'))
    return JsonResponse({"comments": comments})

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        return JsonResponse({"message": "Unliked", "likes": post.likes.count()})
    return JsonResponse({"message": "Liked", "likes": post.likes.count()})

@login_required
def share_post(request, post_id):
    original_post = get_object_or_404(StudentPost, id=post_id)
    if SharedPost.objects.filter(user=request.user, original_post=original_post).exists():
        messages.warning(request, "You have already shared this post.")
        return redirect('post_list')
    SharedPost.objects.create(user=request.user, original_post=original_post)
    messages.success(request, "Post shared successfully!")
    return redirect('post_list')

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return JsonResponse({"message": "Friend request sent"})

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()
    return JsonResponse({"message": "Friend request accepted"})

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return JsonResponse({"message": "Friend request declined"})

def shared_posts_list(request):
    shared_posts = SharedPost.objects.all().order_by('-timestamp')
    return render(request, 'UniSphereApp/shared_posts_list.html', {'shared_posts': shared_posts})
