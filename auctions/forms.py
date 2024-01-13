from django.forms import ModelForm
from .models import Listing, Bid, Comment
from django import forms

class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields =['title', 'description', 'starting_bid', 'image_url', 'category']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'starting_bid': 'Starting Bid',
            'image_url': 'Image URL(optional)',
            'category': 'Category (optional)',
        }

        widgets ={
            'title': forms.TextInput(attrs={"class":"form-control"}),
            'description': forms.Textarea(attrs={"class":"form-control", "rows":3}),
            'starting_bid': forms.NumberInput(attrs={"class":"form-control"}),
            'image_url': forms.URLInput(attrs={"class":"form-control"}),
            'category': forms.Select(attrs={"class":"form-control"}),
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields =['amount']
        labels ={
            'amount': 'Your Bid',
        }

        widgets ={
            'amount':forms.NumberInput(attrs={'step': 0.01, 'class': 'form-control'})
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text':'',
        }

        widgets ={
            'text': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Add Comments', 'rows':1})
        }