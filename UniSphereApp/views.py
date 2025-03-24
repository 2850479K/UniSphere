from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from .models import StudentProfile
from .forms import StudentSearchForm
from .models import ContactRecord, StudentProfile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Project, StudentPost, PostFile, SocietyProfile, StudentProfile
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, SocietyProfileForm, StudentSearchForm, StudentProfileForm
from django.contrib import messages
from .models import Project, StudentPost, PostFile, SocietyProfile, StudentProfile, Comment, Like, Share, FriendRequest, SharedPost
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, SocietyProfileForm, StudentSearchForm, StudentProfileForm, CreateProfileForm, EditProfileForm
from .forms import CreateBasicSocietyProfileForm
from django.http import HttpResponseForbidden


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

    return render(
        request, 
        "UniSphereApp/profile.html", 
        {
            "profile": profile, 
            "projects": projects,  
            "profile_user": profile_user, 
            "is_owner": is_owner,
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


# Society Profile & Student Search

@login_required
def create_society_profile(request):
    existing_profile = SocietyProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = SocietyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Successfully created profile!")
            return redirect(f"/society/profile/{request.user.username}/")
        else:
            messages.error(request, "Please fill in all required fields!")

    else:
        form = SocietyProfileForm()

    return render(request, "society/create_profile.html", {"form": form})

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


@login_required
def society_dashboard(request):
    form = StudentSearchForm(request.GET or None)
    students = StudentProfile.objects.select_related('user').filter(visibility='public')
    show_results = False

    if form.is_valid() and any(form.cleaned_data.values()):
        students = StudentProfile.objects.all()
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
    return render(request, 'society/dashboard.html', {
        'form': form,
        'students': students,
        'show_results': show_results,
    })


@login_required
def contact_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    return render(request, 'society/contact_email.html', {
        'email': student.user.email
    })


@login_required
def save_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    society = request.user.societyprofile

    if student in society.saved_students.all():
        return JsonResponse({"message": "Already Saved"}, status=400)

    society.saved_students.add(student)
    return JsonResponse({"message": "Student Saved", "status": "saved"})

@login_required
def saved_students(request):
    society = request.user.societyprofile
    saved_students = society.saved_students.all()
    return render(request, 'society/saved_students.html', {
        'saved_students': saved_students
    })

@login_required
def unsave_student(request, student_id):
    society = request.user.societyprofile
    student = get_object_or_404(StudentProfile, id=student_id)

    if student in society.saved_students.all():
        society.saved_students.remove(student)

    return redirect('saved_students')


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