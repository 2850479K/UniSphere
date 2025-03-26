from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import (
    Project, StudentPost, PostFile, SocietyProfile, StudentProfile,
    Comment, Like, Share, FriendRequest, SharedPost
)

from .forms import (
    ProjectForm, StudentPostForm, UserRegisterForm,
    SocietyProfileForm, StudentSearchForm, StudentProfileForm,
    CreateProfileForm, EditProfileForm, CreateBasicSocietyProfileForm
)

User = get_user_model()

def home(request):
    form = StudentSearchForm(request.GET or None)
    students = StudentProfile.objects.select_related('user').filter(visibility='public')
    show_results = False

    if form.is_valid() and any(form.cleaned_data.values()):
        username = form.cleaned_data.get('username')
        name = form.cleaned_data.get('name')
        school = form.cleaned_data.get('school')
        course = form.cleaned_data.get('course')
        interests = form.cleaned_data.get('interests')
        skills = form.cleaned_data.get('skills')

        if username:
            students = students.filter(user__username__icontains=username)
        if name:
            students = students.filter(full_name__icontains=name)
        if school:
            students = students.filter(school__icontains=school)
        if course:
            students = students.filter(course__icontains=course)
        if interests:
            students = students.filter(interests__icontains=interests)
        if skills:
            students = students.filter(skills__icontains=skills)

        show_results = True
    posts = StudentPost.objects.filter(
        Q(project__isnull=True) | Q(project__isnull=False, user__studentprofile__visibility='public')
    ).order_by('-timestamp')

    return render(request, 'UniSphereApp/home.html', {
        'posts': posts,
        'form': form,
        'students': students,
        'show_results': show_results,
    })

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
                if user.role == 'society':
                    existing_profile = SocietyProfile.objects.filter(user=user).first()
                    if existing_profile:
                        return redirect('profile', username=user.username)
                    else:
                        return redirect('create_society_profile')
                else:
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

            if user.role == 'society':
                existing_profile = SocietyProfile.objects.filter(user=user).first()
                if not existing_profile:
                    return redirect("/society/create-profile/")
                return redirect(f"/profile/{user.username}/")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
                return JsonResponse({"message": "Login successful!", "redirect": "my_profile"}, status=200)
            messages.success(request, "You have successfully logged in.")
            return redirect('my_profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"error": "Invalid username or password."}, status=400)
            messages.error(request, "Invalid username or password.")

    return render(request, 'UniSphereApp/login.html')

def profile_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = StudentPost.objects.filter(user=user).order_by('-timestamp')
    # Ensure you have a template at UniSphereApp/profile_posts.html
    return render(request, 'UniSphereApp/profile_posts.html', {'profile': user.studentprofile, 'posts': posts})

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

    is_owner = (request.user == profile_user)


    # If profile is private and current user isn't the owner, show a limited view
    if profile.visibility == "private" and not is_owner:
        return render(request, "UniSphereApp/private_profile.html", {"profile": profile})

    # Get up to 6 most recent posts by this user
    recent_posts = StudentPost.objects.filter(user=profile_user).order_by("-timestamp")[:6]

    return render(
        request,
        "UniSphereApp/profile.html",
        {
            "profile": profile,
            "projects": projects,
            "profile_user": profile_user,
            "is_owner": is_owner,
            "recent_posts": recent_posts,  # Pass this to display in the template
        }
    )

@login_required
def my_profile(request):
    return redirect('profile', username=request.user.username)


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

    if profile_user.studentprofile.visibility != 'public' and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this profile.")

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
def create_post(request, project_id=None):
    """
    Create a new post.
    If project_id is provided, the post is created under that project.
    If not, the post is created as a profile post (project is set to None).
    """
    project = get_object_or_404(Project, id=project_id) if project_id else None

    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.project = project  # Will be None for profile posts
            post.save()
            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Post added successfully!")
            if project:
                return redirect('project', project_id=project.id)
            else:
                return redirect('profile', username=request.user.username)
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


def view_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)
    # Render a template that shows the full post details.
    return render(request, 'UniSphereApp/view_post.html', {'post': post})


# Society Profile & Student Search

@login_required
def create_society_profile(request):
    profile, created = SocietyProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CreateBasicSocietyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Basic society profile saved!")
            return redirect('society_profile', username=request.user.username)
    else:
        form = CreateBasicSocietyProfileForm(instance=profile)

    return render(request, 'UniSphereApp/create_profile.html', {'form': form})


@login_required
def edit_society_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user != profile_user or request.user.role != 'society':
        messages.error(request, "You are not allowed to edit this profile.")
        return redirect('/')

    society_profile = get_object_or_404(SocietyProfile, user=profile_user)

    if request.method == 'POST':
        form = SocietyProfileForm(request.POST, request.FILES, instance=society_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(f'/profile/{username}/')
    else:
        form = SocietyProfileForm(instance=society_profile)

    return render(request, 'society/edit_profile.html', {'form': form, 'username': username})

@login_required
def society_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    society_profile = get_object_or_404(SocietyProfile, user=profile_user)

    if profile_user.role != 'society':
        return redirect(f"/profile/{username}/")

    return render(request, "society/society_profile.html", {
        "profile_user": profile_user,
        "society_profile": society_profile,
    })

def search_users(request):
    form = StudentSearchForm(request.GET or None)
    show_results = False
    students = StudentProfile.objects.all()  # Fetch all student profiles
    societies = SocietyProfile.objects.all()  # Fetch all society profiles

    if form.is_valid() and any(form.cleaned_data.values()):
        username = form.cleaned_data.get('username')
        name = form.cleaned_data.get('name')
        school = form.cleaned_data.get('school')
        course = form.cleaned_data.get('course')
        interests = form.cleaned_data.get('interests')
        skills = form.cleaned_data.get('skills')

        # Apply filters to students
        if username:
            students = students.filter(user__username__icontains=username)
        if name:
            students = students.filter(full_name__icontains=name)
        if school:
            students = students.filter(school__icontains=school)
        if course:
            students = students.filter(course__icontains=course)
        if interests:
            students = students.filter(interests__icontains=interests)
        if skills:
            students = students.filter(skills__icontains=skills)

        # Apply filters to societies (make sure you aren't filtering students here)
        if username:
            societies = societies.filter(user__username__icontains=username)
        if name:
            societies = societies.filter(full_name__icontains=name)
        if school:
            societies = societies.filter(company_name__icontains=school)
        if course:
            societies = societies.filter(industry__icontains=course)
        if interests:
            societies = societies.filter(company_description__icontains=interests)

        show_results = True

    return render(request, 'UniSphereApp/search_users.html', {
        'form': form,
        'students': students,
        'societies': societies,
        'show_results': show_results,
    })

@login_required
def contact_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    return render(request, 'society/contact_email.html', {
        'email': student.user.email
    })


@login_required
def join_society(request, society_id):
    society = get_object_or_404(SocietyProfile, id=society_id)
    student_profile = request.user.studentprofile  # Assuming the user is a student
    
    # Add student to the society's members list
    society.members.add(student_profile)
    messages.success(request, f"You have successfully joined {society.company_name}!")

    return redirect('society_profile', username=society.user.username)

@login_required
def members(request):
    society = request.user.societyprofile
    members = society.members.all() 
    return render(request, 'society/members.html', {'members': members})

@login_required
def remove_member(request, student_id):
    society = request.user.societyprofile
    student = get_object_or_404(StudentProfile, id=student_id)

    if student in society.saved_students.all():
        society.saved_students.remove(student)

    return JsonResponse({"message": "Student removed", "status": "removed"})


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


def get_friends(user):
    sent = FriendRequest.objects.filter(from_user=user, accepted=True).values_list('to_user', flat=True)
    received = FriendRequest.objects.filter(to_user=user, accepted=True).values_list('from_user', flat=True)
    friend_ids = list(sent) + list(received)
    return User.objects.filter(id__in=friend_ids)

@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(StudentPost, id=post_id)

    existing_like = Like.objects.filter(user=request.user, post=post)
    liked = False

    if existing_like.exists():
        existing_like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    # If AJAX request, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "liked": liked,
            "likes_count": post.likes.count()
        })

    # Otherwise, fallback to regular redirect
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

@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'UniSphereApp/friend_requests.html', {'request':requests})

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
