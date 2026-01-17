from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    text = models.CharField(max_length=280)
    image = models.ImageField(upload_to='tweets/images/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_tweets', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.tweet}"