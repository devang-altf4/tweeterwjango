from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Tweet

class TweetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_tweet_list_view(self):
        response = self.client.get(reverse('tweet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tweet_list.html')

    def test_tweet_create_view(self):
        response = self.client.get(reverse('tweet_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tweet_form.html')

        response = self.client.post(reverse('tweet_create'), {
            'text': 'Hello World'
        })
        self.assertEqual(response.status_code, 302) # Redirects after success
        self.assertEqual(Tweet.objects.count(), 1)
        self.assertEqual(Tweet.objects.first().text, 'Hello World')

    def test_tweet_edit_view(self):
        tweet = Tweet.objects.create(user=self.user, text='Original Text')
        response = self.client.get(reverse('tweet_edit', args=[tweet.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('tweet_edit', args=[tweet.pk]), {
            'text': 'Updated Text'
        })
        self.assertEqual(response.status_code, 302)
        tweet.refresh_from_db()
        self.assertEqual(tweet.text, 'Updated Text')

    def test_tweet_delete_view(self):
        tweet = Tweet.objects.create(user=self.user, text='To Delete')
        response = self.client.get(reverse('tweet_delete', args=[tweet.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('tweet_delete', args=[tweet.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tweet.objects.count(), 0)