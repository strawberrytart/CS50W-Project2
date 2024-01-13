from django.contrib import admin

from .models import User,Category, Listing, Bid,Comment
# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id','title','starting_bid','category', 'owner', 'created_at', 'is_active')
    filter_horizontal =('watchlist',)
    ordering =['id']

class CommentAdmin(admin.ModelAdmin):
    list_display =('commenter', 'text', 'listing', 'timestamp')
    ordering = ['-timestamp',]

class BidAdmin(admin.ModelAdmin):
    list_display =['bidder','amount', 'listing', 'timestamp']
    ordering = []

admin.site.register(Listing, ListingAdmin)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)