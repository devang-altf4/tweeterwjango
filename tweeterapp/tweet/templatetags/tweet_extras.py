from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse
import re

register = template.Library()

@register.filter
def linkify_tweet(value):
    # Escape the content first to prevent XSS
    value = escape(value)
    
    # Linkify hashtags: #tag -> search link
    def replace_hashtag(match):
        hashtag = match.group(0) # e.g., #django
        tag_name = hashtag[1:]   # e.g., django
        # URL encode the # as %23 so it's treated as a query param, not an anchor
        url = reverse('tweet_list') + f'?q=%23{tag_name}'
        return f'<a href="{url}" class="text-blue-500 hover:underline">{hashtag}</a>'

    value = re.sub(r'#\w+', replace_hashtag, value)
    
    # Linkify mentions: @user -> profile link
    def replace_mention(match):
        mention = match.group(0) # e.g., @devang
        username = mention[1:]   # e.g., devang
        try:
            url = reverse('profile', args=[username])
            return f'<a href="{url}" class="text-blue-500 hover:underline">{mention}</a>'
        except:
            return mention

    value = re.sub(r'@\w+', replace_mention, value)
    
    return mark_safe(value)