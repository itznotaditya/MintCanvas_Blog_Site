# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Post, Comment  # Removed Category and Tag imports
from .forms import SignUpForm, PostForm, CommentForm
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to the blog!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)  # Show 5 posts per page.

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'home.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid() and request.user.is_authenticated:
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form, 'action': 'Create'})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.author:
        messages.error(request, "You can't edit this post!")
        return redirect('post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_form.html', {'form': form, 'action': 'Edit'})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user != post.author:
        messages.error(request, "You can't delete this post!")
        return redirect('post_detail', slug=slug)

    # Delete the post
    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect('home')

@login_required
def profile_edit(request, username):
    user = get_object_or_404(User, username=request.user.username)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)  # Redirect back to profile view
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'blog/profile_edit.html', {'form': form})



def profile_view(request, username):
    user = get_object_or_404(User, username=username)  # Make sure you import the User model correctly
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    context = {
        'profile': profile,
        'posts': posts,
    }
    return render(request, 'blog/profile_view.html', context)