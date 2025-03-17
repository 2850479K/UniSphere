from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentPost, PostFile
from .forms import StudentPostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm
from .models import RecruiterProfile
from .forms import RecruiterProfileForm
from django.db.models import Q
from .models import StudentProfile, SharedPost 
from .forms import StudentSearchForm
from django.http import JsonResponse
from .models import Comment, Like, Share, FriendRequest

#view to display all post/projects
def post_list(request):
    posts = StudentPost.objects.all().order_by('-timestamp')
    return render(request, 'UniSphereApp/post_list.html', {'posts': posts})

#view for creating a new post/project
@login_required
def create_post(request):
    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES)
        #get list of uploaded files
        files = request.FILES.getlist('files')

        if form.is_valid():
            post = form.save(commit=False)
            #assign the current user to the post
            post.user = request.user
            post.save()

            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Project posted successfully.")
            return redirect('post_list')
    else:
        form = StudentPostForm()
    return render(request, 'UniSphereApp/create_post.html', {'form':form})

# view and edit a specific project
@login_required
def view_post(request, project_id):
    #get project and return an error if it does not exist
    post = get_object_or_404(StudentPost, id=project_id)
    #only allow owner of post to edit
    if post.user != request.user:
        messages.error(request, "You are not authorised to edit this post.")
        return redirect('post_list')
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            post.delete()
            messages.success(request, "Post successfully deleted")
            return redirect('post_list')
        
        form = StudentPostForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('files')

        if form.is_valid():
            form.save()
            #add new files
            for file in files:
                PostFile.objects.create(post=post, file=file)
            messages.success(request, "Post updated successfully.")
            return redirect('view_post', project_id=post.id)
    else:
        form = StudentPostForm(instance=post)
    return render(request,'UniSphereApp/view_post.html', {'form':form,'post':post})

@login_required
def edit_post(request, project_id):
    post = get_object_or_404(StudentPost, id=project_id)

    # Only allow the owner to edit the post
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('view_post', project_id=project_id)

    if request.method == 'POST':
        form = StudentPostForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('files')

        if form.is_valid():
            form.save()

            # Add new files
            for file in files:
                PostFile.objects.create(post=post, file=file)

            messages.success(request, "Post updated successfully.")
            return redirect('view_post', project_id=post.id)

    else:
        form = StudentPostForm(instance=post)

    return render(request, 'UniSphereApp/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, project_id):
    post = get_object_or_404(StudentPost, id=project_id)

    # Only allow the owner to delete the post
    if post.user != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('view_post', project_id=project_id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post successfully deleted.")
        return redirect('post_list')

    return redirect('view_post', project_id=project_id)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']  # Saves the role
            user.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'UniSphereApp/register.html', {'form': form})

def home(request):
    return render(request, 'UniSphereApp/home.html')


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

@login_required
def profile(request):
    return render(request, 'UniSphereApp/profile.html')



#views for comment, share, friendrequest, and like

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(StudentPost, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('view_post', project_id=post.id)

@login_required
def get_comments(request, post_id):
    """Return comments for a post in JSON format"""
    post = get_object_or_404(StudentPost, id=post_id)
    comments = list(post.comments.values('user__username', 'content', 'created_at'))
    return JsonResponse({"comments": comments})
    
# like and unlike post
@login_required
def toggle_like(request, post_id):
    """Like or Unlike a Post"""
    post = get_object_or_404(StudentPost, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()  # If already liked, unlike the post
        return JsonResponse({"message": "Unliked", "likes": post.likes.count()})

    return JsonResponse({"message": "Liked", "likes": post.likes.count()})

def share_post(request, post_id):
    original_post = get_object_or_404(StudentPost, id=post_id)

    # Prevent users from sharing the same post multiple times
    if SharedPost.objects.filter(user=request.user, original_post=original_post).exists():
        messages.warning(request, "You have already shared this post.")
        return redirect('post_list')

    # Create the shared post
    SharedPost.objects.create(user=request.user, original_post=original_post)
    messages.success(request, "Post shared successfully!")
    return redirect('post_list')

@login_required
def send_friend_request(request, user_id):
    """Send a friend request to another user"""
    to_user = get_object_or_404(settings.AUTH_USER_MODEL, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return JsonResponse({"message": "Friend request sent"})

@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()
    return JsonResponse({"message": "Friend request accepted"})

@login_required
def decline_friend_request(request, request_id):
    """Decline a friend request"""
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return JsonResponse({"message": "Friend request declined"})

def shared_posts_list(request):
    """View shared posts"""
    shared_posts = SharedPost.objects.all().order_by('-timestamp')
    return render(request, 'UniSphereApp/shared_posts_list.html', {'shared_posts': shared_posts})