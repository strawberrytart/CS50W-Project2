from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length= 50)

    def __str__(self):
        return self.name
    
    

    class Meta:
        verbose_name_plural = "Categories"



class Listing(models.Model):
    title = models.CharField(max_length =30)
    description = models.TextField(max_length = 180)
    starting_bid = models.DecimalField(max_digits =10, decimal_places = 2)
    image_url = models.URLField(blank=True, null= True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name ="listings")

    owner = models.ForeignKey(User, on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, null = True, related_name ="watchlist_listings")
    winner = models.ForeignKey(User,blank=True, null=True, on_delete=models.SET_NULL, related_name="wins")

    def __str__(self):
        return self.title

class Bid(models.Model):
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    bidder = models.ForeignKey(User, on_delete = models.CASCADE,related_name="bids")
    timestamp = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{ self.bidder } places a bid of { self.amount } on { self.listing }"


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete = models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete= models.CASCADE,related_name="comments")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter}: {self.text}"


    

