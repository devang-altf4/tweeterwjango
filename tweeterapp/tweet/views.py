from django.shortcuts import redirect, render, get_object_or_404
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    return render(request, 'index.html')

def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        tweets = tweets.filter(text__icontains=query)
    return render(request, 'tweet_list.html', {'tweets': tweets})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=profile_user).order_by('-created_at')
    return render(request, 'profile.html', {'profile_user': profile_user, 'tweets': tweets})

@login_required
def my_tweets(request):
    tweets = Tweet.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tweet_list.html', {'tweets': tweets})

def tweet_detail(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.all().order_by('-created_at')
    form = CommentForm()
    return render(request, 'tweet_detail.html', {'tweet': tweet, 'comments': comments, 'form': form})

@login_required
def tweet_like(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)
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
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Tweeter, {user.username}!')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})