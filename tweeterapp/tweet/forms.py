from django import forms
from .models import Tweet, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['text', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-200 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm resize-none',
                'rows': '3',
                'placeholder': 'Post your reply...'
            })
        }
        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')