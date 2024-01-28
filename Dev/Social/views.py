from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse,resolve
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *
import json
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    return render(request,'home.html')

def frontpage(request):
    return render(request,'web.html')

# List Posts in Feed
@login_required
def feed(request):
    user = request.user
    posts = Stream.objects.filter(user=user)
    group_ids = [post.post_id for post in posts]
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    for post in post_items:
        post.user_has_liked = post.likes.filter(id=user.id).exists()

    profile = Profile.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If it's an AJAX request, return post comments in JSON format
        comments_data = []
        for post in post_items:
            comments_data.append({
                'post_id': post.id,
                'comments': [{'text': comment.text} for comment in post.comments.all()]
            })
        return JsonResponse({'comments_data': comments_data})
    # Fetch comments for each post using set()
    for post in post_items:
        post.comments.set(Comment.objects.filter(post=post).order_by('created'))
    comment_form = CommentForm()
    context = {
        'post_items': post_items,
        'profile': profile,
        'comment_form': comment_form,
    }
    return render(request, 'feed.html', context)

#Form submission with AJAX
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # Associate the comment with the logged-in user
            comment.post = post
            comment.save()
            return JsonResponse({'success': True, 'message': 'Comment added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

#Fetching comments with AJAX
def fetch_post_comments(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post)
        comment_data = []
        for comment in comments:
            comment_data.append({
                'user': {
                    'username': comment.user.username,
                    'profile_picture': comment.user.profile.image.url if comment.user.profile.image else None,
                },
                'text': comment.text,
            })
        return JsonResponse({'comments': comment_data})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

#Search
def search(request):
    q = request.GET.get('search') if request.GET.get('search') != None else ""
    user_results = User.objects.filter( Q(username__istartswith=q) | Q(profile__full_name__istartswith=q) ) 
    tag_results = Tag.objects.filter( Q(title__istartswith=q))
    context = {
        'userresults' : user_results,
        'tagresults' : tag_results
    }
    return render(request, "find.html", context)

#Signup
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        fname = request.POST['fname']
        username = request.POST['username']
        pass1 = request.POST['pass1']
        myuser = User.objects.create_user(username,email,pass1)
        list1 = fname.split(" ")
        firstn = list1[0]
        lastn = list1[1]
        myuser.first_name = firstn
        myuser.last_name = lastn
        myuser.save()
        messages.success(request, "Your account has been succesfully created.")
        return redirect('signin')
    return render(request,'signup.html')

#Signin
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        user = authenticate(request,username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect(feed)
        else:
            messages.error(request, "Bad Credentials !")
    storage = messages.get_messages(request)
    storage.used = True
    return render(request,'signin.html')

#Signout 
def signout(request):
    logout(request)
    messages.success(request, "Logged out Successfully")
    return redirect('frontpage')

    
#Create New Post
@login_required
def NewPost(request):
    user = request.user.id
    tags_objs = []

    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = request.POST.get('caption')
            tag_form = form.cleaned_data.get('tag')
            tags_list = list(tag_form.split(' '))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user_id=user)
            p.tag.set(tags_objs)
            p.save()
        return redirect('feed')
    else:
        form = NewPostForm()
    context = {
        'form': form
    }
    return render(request, 'newpost.html', context)

#Detailed Post page
def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = get_object_or_404(Profile, user=post.user)
    user = request.user
    post.user_has_liked = post.likes.filter(id=user.id).exists()
    context = {
        'post' : post,
        'profile' : profile,
    }
    return render(request, 'post-details.html', context)


#Tag filtering posts
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tag=tag).order_by('-posted')
    context = {
        'tag' : tag,
        'posts' : posts
    }
    return render(request, 'tags.html', context)

#Like with Ajax
def like(request):
    data = json.loads(request.body)
    id = data["id"]
    post = Post.objects.get(id=id)
    checker = 0

    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            checker = 0
        else:
            post.likes.add(request.user)
            checker = 1
    likes = post.likes.count()
    info = {
        "check": checker,
        "num_of_likes": likes
    }
    return JsonResponse(info, safe=False)

#Savepost
def saved(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)
    if profile.saved.filter(id=post_id).exists():
        profile.saved.remove(post)
    else:
        profile.saved.add(post)
    return HttpResponseRedirect(reverse('feed'))


def test(request):
    user = request.user
    posts = Post.objects.all().order_by('-posted')
    return render(request,'test.html', {'post_items':posts})


#Profile
def profile(request,username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    if url_name == 'profilee':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.saved.all()
    
    #Tracking Profile Stats
    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    follower_count = Follow.objects.filter(following=user).count()
    
    #Follow status
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    #pagination
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)
    context = {
        'posts_paginator' : posts_paginator,
        'profile' : profile,
        'posts' : posts,
        'url_name' : url_name,
        'post_count' : post_count,
        'following_count' : following_count,
        'follower_count' : follower_count,
        'follow_status' : follow_status
    }
    return render(request, 'profile.html', context)

#Our Profile
@login_required
def my_profile(request):
    username = request.user.username
    return redirect('profilee', username=username)

def navbar(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    context = {
        'profile' : profile
    }
    return render(request, 'header.html', context)

#Follow function
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)
    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        if int(option) == 0 :
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.filter(user=following)[:10]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profilee', args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profilee', args=[username]))

#Edit profile
def editProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user_id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profilee', username=request.user.username)
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
    }
    return render(request, 'edit-profile.html', context)


def createtweet(request):
    if request.method=="POST":
        tweet = request.POST['tweet']
        Tweet.objects.create(user=request.user,tweet=tweet)
    return render(request, 'newtweet.html')

# def edittweet(request,id):
#     if not request.user.is_authenticated:
#         redirect('signin')
#     r=Tweet.objects.get(id=id)
#     if request.method=="POST":
#         form=TweetForm(request.POST,instance=r)
#         if form.is_valid():
#             twt_form=form.save(commit=False)
#             twt_form.user=request.user
#             twt_form.save()
#             return redirect(userprofile)
#         else:
#             return HttpResponse("Form not validated")
#     form=TweetForm(instance=r)
#     return render(request,edittweet.html',{'form':form})


# def deletetweet(request,id):
#     if not request.user.is_authenticated:
#         redirect('/user/login')    
#     if request.method=="POST":
#         twt=Tweet.objects.get(id=id)
#         twt.delete()
#         return redirect(userprofile)
        
#     q=Tweet.objects.get(id=id)
#     return render(request,'Tweet/deletetweet.html',{'context':q})


# def tweet_replies(request,id):
#     a=Tweet.objects.get(id=id)
#     b=reversed(a.reply_set.all())
#     return render(request,'Tweet/demo.html',{'tweet':a,'reply':b})
