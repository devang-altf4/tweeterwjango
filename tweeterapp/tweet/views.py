from django.shortcuts import redirect, render, get_object_or_404
from .models import Tweet, Profile, Tag
from .forms import TweetForm, UserRegistrationForm, CommentForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.text import slugify
from django.http import JsonResponse

def home(request):
    return render(request, 'index.html')

def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        # If searching for a hashtag (e.g. #django), filter by the tag name
        if query.startswith('#'):
            tag_slug = slugify(query[1:])
            tweets = tweets.filter(tags__slug=tag_slug)
        else:
            tweets = tweets.filter(text__icontains=query)
    
    paginator = Paginator(tweets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    who_to_follow = []
    if request.user.is_authenticated:
        # Get all profiles excluding the current user's profile
        all_profiles = Profile.objects.exclude(user=request.user)
        # Filter out profiles the user is already following
        following_ids = request.user.profile.follows.values_list('id', flat=True)
        who_to_follow = all_profiles.exclude(id__in=following_ids).order_by('?')[:3]

    # Get trending tags (top 5 by number of tweets)
    trending_tags = Tag.objects.annotate(num_tweets=Count('tweets')).order_by('-num_tweets')[:5]

    return render(request, 'tweet_list.html', {
        'tweets': page_obj, 
        'who_to_follow': who_to_follow, 
        'page_obj': page_obj,
        'trending_tags': trending_tags
    })

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    tab = request.GET.get('tab', 'tweets')
    if tab == 'likes':
        tweets = profile_user.liked_tweets.all().order_by('-created_at')
    else:
        tweets = Tweet.objects.filter(user=profile_user).order_by('-created_at')
    
    paginator = Paginator(tweets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check follow status
    is_following = False
    if request.user.is_authenticated:
        if request.user.profile.follows.filter(id=profile_user.profile.id).exists():
            is_following = True
            
    return render(request, 'profile.html', {
        'profile_user': profile_user, 
        'tweets': page_obj,
        'page_obj': page_obj,
        'is_following': is_following,
        'active_tab': tab
    })

@login_required
def follow_toggle(request, pk):
    profile_to_toggle = get_object_or_404(Profile, pk=pk)
    if request.user.profile == profile_to_toggle:
        messages.warning(request, "You cannot follow yourself.")
        return redirect('profile', username=request.user.username)
        
    is_following = False
    if request.user.profile.follows.filter(pk=profile_to_toggle.pk).exists():
        request.user.profile.follows.remove(profile_to_toggle)
        is_following = False
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            messages.info(request, f"You have unfollowed {profile_to_toggle.user.username}.")
    else:
        request.user.profile.follows.add(profile_to_toggle)
        is_following = True
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            messages.success(request, f"You are now following {profile_to_toggle.user.username}.")
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'is_following': is_following,
            'followers_count': profile_to_toggle.followed_by.count(),
            'following_count': profile_to_toggle.follows.count()
        })
        
    return redirect('profile', username=profile_to_toggle.user.username)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'edit_profile.html', context)

@login_required
def my_tweets(request):
    tweets = Tweet.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(tweets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'tweet_list.html', {'tweets': page_obj, 'page_obj': page_obj})

def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all().order_by('-created_at')
    form = CommentForm()
    return render(request, 'tweet_detail.html', {'tweet': tweet, 'comments': comments, 'form': form})

@login_required
def tweet_like(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    liked = False
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': tweet.total_likes()})
    
    return redirect(request.META.get('HTTP_REFERER', 'tweet_list'))

@login_required
def tweet_comment(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.tweet = tweet
            comment.save()
            messages.success(request, 'Your reply has been posted.')
    return redirect('tweet_detail', pk=pk)

@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Your tweet has been posted!')
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_edit(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your tweet has been updated!')
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_delete(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.method == 'POST':
        tweet.delete()
        messages.success(request, 'Tweet deleted successfully.')
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile_picture = form.cleaned_data.get('profile_picture')
            if profile_picture:
                user.profile.profile_picture = profile_picture
                user.profile.save()
            login(request, user)
            messages.success(request, f'Welcome to Tweeter, {user.username}!')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})