import sqlite3
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db import transaction
from .models import Post, Comment
from .forms import PostForm, CommentForm, SignUpForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@login_required
def homePageView(request):
    posts = Post.objects.all()
    mypost = Post.objects.filter(author=request.user).count()
    is_searched = False
    return render(request, 'index.html', {'Posts': posts, 'Mypost': mypost, 'is_searched': is_searched})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/signup-reset')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def signup_reset(request):
    cur_user = request.user
    if request.method == 'POST':
        if request.POST.get('reset') == '':
            return render(request, 'signup_reset.html', {'blank':True})
        cur_user.last_name = request.POST.get('reset')
        # To fix 'Cryptographic Failures'
        #cur_user.last_name = make_password(request.POST.get('reset'))
        cur_user.save()
        return redirect('/')
    else:
        return render(request, 'signup_reset.html')
    
def password_reset(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            try:
                user = User.objects.get(username=request.POST.get('username'), last_name=request.POST.get('reset'))
                # To fix 'Cryptographic Failures'
                #user = User.objects.get(username=request.POST.get('username'))
                #if not check_password(request.POST.get('reset'), user.last_name):
                    #return render(request, 'password_reset.html', {'notloggedin': True, 'wrongreset': True})
            except User.DoesNotExist:
                return render(request, 'password_reset.html', {'notloggedin': True, 'doesntexist': True})
            if request.POST.get('new_pw1') == request.POST.get('new_pw2'):
                try:
                    validate_password(request.POST.get('new_pw1'))
                    user.set_password(request.POST.get('new_pw1'))
                    user.save()
                    return redirect('/')
                except ValidationError as e:
                    return render(request, 'password_reset.html', {'notloggedin': True, 'notvalid': True, 'errormsg': e})
            else:
                return render(request, 'password_reset.html', {'notloggedin': True, 'doesntmatch': True})
        else:
            user = request.user
            if request.POST.get('new_pw1') == request.POST.get('new_pw2'):
                try:
                    validate_password(request.POST.get('new_pw1'))
                    user.set_password(request.POST.get('new_pw1'))
                    user.save()
                    return redirect('/')
                except ValidationError as e:
                    return render(request, 'password_reset.html', {'notloggedin': False, 'notvalid': True, 'errormsg': e})
            else:
                return render(request, 'password_reset.html', {'notloggedin': False, 'doesntmatch': True})
    else:
        if not request.user.is_authenticated:
            return render(request, 'password_reset.html', {'notloggedin': True})
        else:
            return render(request, 'password_reset.html', {'notloggedin': False})
            

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', post_id=post.pk)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.pk)
    else:
        comments = Comment.objects.filter(post=post_id)
        is_author = post.author == request.user
    return render(request, 'post_detail.html', {'post': post, 'form': CommentForm(), 'Comments': comments, 'is_author': is_author})

@login_required
def post_update(request, post_id):
    post = Post.objects.get(pk=post_id)
    #if post.author == request.user:        # To fix 'Broken Access Control'
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post)
        return render(request, 'post_update.html', {'form': form})
    #else:
        #return redirect('post_detail', post_id=post.pk)        # To fix 'Broken Access Control'

@login_required
def post_delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    #if post.author == request.user:        # To fix 'Broken Access Control'
    if request.method == 'POST':
        post.delete()
        return redirect('/')
    else:
        return render(request, 'post_delete_confirm.html', {'post': post})
    #else:
        #return redirect('post_detail', post_id=post.pk)        # To fix 'Broken Access Control'


def post_search(request):
    search = request.GET.get('search')
    posts = Post.objects.all()
    mypost = Post.objects.filter(author=request.user).count()
    conn = sqlite3.connect('src/db.sqlite3')
    cursor = conn.cursor()
    response = cursor.execute("SELECT id, title FROM pages_post WHERE title LIKE '%" + search + "%' or content LIKE '%" + search + "%'").fetchall()
    # To fix 'Injection'
    #response = cursor.execute("SELECT id, title FROM pages_post WHERE title LIKE ? or content LIKE ?", (f'%{search}%', f'%{search}%', )).fetchall()
    is_searched = True
    return render(request, 'index.html', {'Posts': posts, 'Mypost': mypost, 'result': response, 'is_searched': is_searched})