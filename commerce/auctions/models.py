from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.forms import ModelForm, Textarea, DateTimeInput, TextInput, NumberInput
from django import forms
from django.utils.translation import gettext as _


class User(AbstractUser):
    pass


class Listing(models.Model):
    
    CategoryType = models.TextChoices('CategoryType', 
        ['ELECTRONICS',
        'FASHION',
        'HOME_&_OFFICE',
        'TOYS',
        'SPORTING_GOODS',
        'BABY_PRODUCTS',
        'OTHER']
    ) 
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=256)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CategoryType.choices, default='ELECTRONICS')
    image_url = models.URLField(blank="True")
    active = models.BooleanField(default="True")
    
    def __str__(self):
        return f'{self.title}'
    

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'${self.amount} - {self.listing.title}'

class Comment(models.Model): 
    commentor = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.content[:25]}...'

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist")


class NewListingForm(ModelForm):
    class Meta:
        exclude = ['created_by', 'active']
        model = Listing
        widgets = {
              'description': Textarea(attrs={'cols': 70, 'rows': 7}),
              'starting_bid': NumberInput(attrs={'min': 0})
          }


class BiddingForm(ModelForm):
    class Meta:
        
        
        fields = ['amount']
        # widgets = {
        #     'amount': NumberInput(attrs={'min': Bid.objects.filter()}),
        # }
        help_texts = {
            'amount': _('Enter an amount to bid.'),
        }

        error_messages = {
            'amount': {
                'min': _('Amount should be larger than: ')
            }
        }


class BidForm(forms.Form):
    bidder_id = forms.IntegerField(min_value=0)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)



class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['commentor', 'listing']
        widgets = {
            'content': Textarea
        }
"""    
def __init__(self, *args, **kwargs):
super().__init__(*args, **kwargs)
self.fields['name'].widget.attrs.update({'class': 'special'})
self.fields['comment'].widget.attrs.update(size='40')

"""