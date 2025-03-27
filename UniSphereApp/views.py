from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.db.models import Q
from .models import Project, StudentPost, PostFile, StudentProfile, Comment, Like, Share, FriendRequest, Repost, SocietyProfile
from .forms import ProjectForm, StudentPostForm, UserRegisterForm, SearchUserForm, StudentProfileForm, CreateProfileForm, EditProfileForm, SocietyProfileForm, SocietyCreateProfileForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()

def home(request):
    if not request.user.is_authenticated:
        return redirect('welcomepage')
    posts = StudentPost.objects.filter(
        Q(project__isnull=True) | Q(project__isnull=False, user__studentprofile__visibility='public')
    ).order_by('-timestamp')
    return render(request, 'UniSphereApp/home.html', {'posts': posts})

def welcomepage(request):
    recent_posts = StudentPost.objects.filter(project__isnull=True).order_by('-timestamp')[:2]
    return render(request, 'UniSphereApp/welcomepage.html', {'recent_posts': recent_posts})

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
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

    if user.role == 'student':
        profile = get_object_or_404(StudentProfile, user=user)
    elif user.role == 'society':
        profile = get_object_or_404(SocietyProfile, user=user)
    else:
        profile = None

    return render(request, 'UniSphereApp/profile_posts.html', {
        'profile': profile,
        'posts': posts
    })

@login_required
def create_profile(request):
    if request.user.role == 'student':
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = CreateProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Student profile created successfully!")
                return redirect('profile', username=request.user.username)
        else:
            form = CreateProfileForm(instance=profile)
        return render(request, 'UniSphereApp/create_profile.html', {'form': form})

    elif request.user.role == 'society':
        profile, created = SocietyProfile.objects.get_or_create(user=request.user)

        if created:
            profile.contact_email = request.user.email
            profile.save()

        if request.method == 'POST':
            form = SocietyCreateProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Society profile created successfully!")
                return redirect('profile', username=request.user.username)
        else:
            form = SocietyCreateProfileForm(instance=profile)

        return render(request, 'UniSphereApp/create_profile.html', {'form': form})



def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user.is_authenticated and request.user == profile_user
    is_friend = False
    friend_request_sent = False

    if profile_user.role == 'student':
        profile, created = StudentProfile.objects.get_or_create(user=profile_user)
        projects = Project.objects.filter(user=profile_user).order_by("-timestamp")[:5]
        recent_posts = StudentPost.objects.filter(user=profile_user).order_by("-timestamp")[:6]
        user_friends = profile.friends.all()

        if request.user.is_authenticated and not is_owner and request.user.role == 'student':
            try:
                current_student_profile = StudentProfile.objects.get(user=request.user)
                if profile in current_student_profile.friends.all():
                    is_friend = True
                elif FriendRequest.objects.filter(
                    from_user=request.user,
                    to_user=profile_user,
                    status='pending' 
                ).exists():
                    friend_request_sent = True
            except StudentProfile.DoesNotExist:
                pass  

        if profile.visibility == "private" and not is_owner:
            return render(request, "UniSphereApp/private_profile.html", {"profile": profile})

        return render(request, "UniSphereApp/student_profile.html", {
            "profile": profile,
            "projects": projects,
            "profile_user": profile_user,
            "is_owner": is_owner,
            "recent_posts": recent_posts,
            "is_friend": is_friend,
            "friend_request_sent": friend_request_sent,
            "user_friends": user_friends,
        })

    elif profile_user.role == 'society':
        profile, created = SocietyProfile.objects.get_or_create(user=profile_user)
        projects = Project.objects.filter(user=profile_user).order_by("-timestamp")[:5]
        recent_posts = StudentPost.objects.filter(user=profile_user).order_by("-timestamp")[:6]

        is_member = False
        student_profile = None

        if request.user.is_authenticated and request.user.role == 'student':
            student_profile = StudentProfile.objects.filter(user=request.user).first()
            if student_profile:
                is_member = profile.members.filter(id=student_profile.id).exists()

                if request.method == 'POST':
                    action = request.POST.get('action')
                    if action == 'join' and not is_member:
                        profile.members.add(student_profile)
                        is_member = True
                    elif action == 'leave' and is_member:
                        profile.members.remove(student_profile)
                        is_member = False

        return render(request, "UniSphereApp/society_profile.html", {
            "profile": profile,
            "profile_user": profile_user,
            "is_owner": is_owner,
            "projects": projects,
            "recent_posts": recent_posts,
            "is_member": is_member,
        })

@login_required
def remove_friend(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)

        try:
            request.user.studentprofile.friends.remove(target_user.studentprofile)
            target_user.studentprofile.friends.remove(request.user.studentprofile)

            messages.success(request, f"You removed {target_user.username} from your friends.")
        except Exception as e:
            messages.error(request, "Something went wrong while removing the friend.")

        return redirect('friend_requests') 

    return redirect('friend_requests')

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
            post.project = project  
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
    return render(request, 'UniSphereApp/view_post.html', {'post': post})


def search_users(request):
    students = []
    societies = []
    show_results = False

    username = request.GET.get("username", "").strip()
    name = request.GET.get("name", "").strip()
    school = request.GET.get("school", "").strip()
    course = request.GET.get("course", "").strip()
    interests = request.GET.get("interests", "").strip()
    skills = request.GET.get("skills", "").strip()
    society_name = request.GET.get("society_name", "").strip()
    category = request.GET.get("category", "").strip()
    description = request.GET.get("description", "").strip()
    contact_email = request.GET.get("contact_email", "").strip()

    if any([username, name, school, course, interests, skills, society_name, category, description, contact_email]):
        show_results = True

        student_filters = Q()
        if username:
            student_filters &= Q(user__username=username)
        if name:
            student_filters &= Q(full_name=name)
        if school:
            student_filters &= Q(school=school)
        if course:
            student_filters &= Q(course=course)
        if interests:
            student_filters &= Q(interests=interests)
        if skills:
            student_filters &= Q(skills=skills)

        if student_filters:  
            students = StudentProfile.objects.filter(student_filters)

        society_filters = Q()
        if username:
            society_filters &= Q(user__username=username)
        if society_name:
            society_filters &= Q(society_name=society_name)
        if category:
            society_filters &= Q(category=category)
        if description:
            society_filters &= Q(description=description)
        if contact_email:
            society_filters &= Q(contact_email=contact_email)

        if any([username, society_name, category, description, contact_email]):
            societies = SocietyProfile.objects.filter(society_filters)

    return render(request, "UniSphereApp/search_users.html", {
        "show_results": show_results,
        "students": students,
        "societies": societies,
    })

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

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "liked": liked,
            "likes_count": post.likes.count()
        })

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


@require_POST
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        if created:
            return JsonResponse({"message": "Friend request sent"})
        else:
            return JsonResponse({"message": "Friend request already exists"}, status=400)
    return JsonResponse({"error": "Cannot send request to yourself"}, status=400)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, status=FriendRequest.PENDING)
    friend_request.status = FriendRequest.ACCEPTED
    friend_request.save()

    friend_request.from_user.studentprofile.friends.add(friend_request.to_user.studentprofile)
    friend_request.to_user.studentprofile.friends.add(friend_request.from_user.studentprofile)

    return redirect('friend_requests')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('friend_requests', username=request.user.username)

@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.PENDING)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    is_owner = True 

    return render(request, 'UniSphereApp/friend_requests.html', {
        'requests': requests,
        'is_owner': is_owner,
        'student_profile': student_profile,
    })

@login_required
def share_post(request, post_id):
    original_post = get_object_or_404(StudentPost, id=post_id)

    if Repost.objects.filter(user=request.user, original_post=original_post).exists():
        messages.warning(request, "You have already shared this post.")
    else:
        Repost.objects.create(user=request.user, original_post=original_post)
        messages.success(request, "Post shared successfully!")

    return redirect('user_reposts', username=request.user.username)

def user_reposts(request, username):
    profile_user = get_object_or_404(User, username=username)
    reposts = Repost.objects.filter(user=profile_user).order_by('-timestamp')

    return render(request, 'UniSphereApp/user_reposts.html', {
        'profile_user': profile_user,
        'reposts': reposts,
    })

@login_required
def edit_society_profile(request):
    profile = get_object_or_404(SocietyProfile, user=request.user)

    if request.user != profile.user:
        messages.error(request, "You are not authorized to edit this profile.")
        return redirect('profile', username=request.user.username)

    if request.method == 'POST':
        form = SocietyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()

            if profile.contact_email:
                request.user.email = profile.contact_email
                request.user.save()

            messages.success(request, "Society profile updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        form = SocietyProfileForm(instance=profile)

    return render(request, 'UniSphereApp/edit_society.html', {'form': form})

@login_required
def contact_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.role == 'student':
        profile = get_object_or_404(StudentProfile, user=user)
        email = profile.user.email  
    elif user.role == 'society':
        profile = get_object_or_404(SocietyProfile, user=user)
        email = profile.contact_email 
    
    return render(request, 'UniSphereApp/contact_email.html', {'email': email})

def society_members(request, society_username):
    society_user = get_object_or_404(User, username=society_username)
    society = get_object_or_404(SocietyProfile, user=society_user)
    members = society.members.all()

    is_member = False
    student_profile = None

    if request.user.is_authenticated and request.user.role == 'student':
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        is_member = society.members.filter(id=student_profile.id).exists()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'leave' and is_member:
            society.members.remove(student_profile)
            messages.success(request, "You have left the society.")
            return redirect('society_members', society_username=society_username)

        elif action == 'join' and not is_member:
            society.members.add(student_profile)
            messages.success(request, "You have joined the society.")
            return redirect('society_members', society_username=society_username)

        elif action == 'kick' and request.user == society_user and request.user.role == 'society':
            student_id = request.POST.get('student_id')
            student_to_remove = StudentProfile.objects.filter(id=student_id).first()
            if student_to_remove:
                society.members.remove(student_to_remove)
                messages.success(request, f"{student_to_remove.full_name or student_to_remove.user.username} was removed.")
            return redirect('society_members', society_username=society_username)

    return render(request, 'UniSphereApp/society_members.html', {
        'society': society,
        'members': members,
        'is_member': is_member,
    })
    

@login_required
def joined_societies(request, username):
    student_user = get_object_or_404(User, username=username, role='student')
    student_profile = get_object_or_404(StudentProfile, user=student_user)
    societies = student_profile.joined_societies.all()

    return render(request, 'UniSphereApp/joined_societies.html', {
        'student_profile': student_profile,
        'societies': societies,
    })
