
from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentPost, PostFile
from .forms import StudentPostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm

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
            user.role = form.cleaned_data['role']
            user.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'UniSphereApp/register.html', {'form': form})

def home(request):
    return render(request, 'UniSphereApp/home.html')

