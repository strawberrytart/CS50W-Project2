from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import CreateListingForm, BidForm, CommentForm
from django.db.models import Max
from .models import User, Listing, Bid, Category


def index(request):
    return render(request, "auctions/index.html",{
        #Get a queryset of Listings that is active and order them by creation date in descending order
        "listings": Listing.objects.filter(is_active=True).order_by('-created_at'),
    })


def listing(request,listing_id):
    
    #Get the listing (or model instance of Listing) whose id is 
    listing = Listing.objects.get(id=listing_id)
    #Get a queryset of watchlist of listing, check whether the user exists in the queryset() 
    is_watched = listing.watchlist.filter(pk=request.user.pk).exists()
    #Get a queryset of all the bids of Listing and calculate the length of the queryset
    #Checks if listing has any bids at all 
    bid_count = listing.bids.all().count()
    #if there is bid, show current maximum bid price
    if bid_count > 0:
        display_bid = round(listing.bids.all().aggregate(Max('amount'))['amount__max'],2)
    #if there is no bid, show starting bid_price
    else:
        display_bid = round(listing.starting_bid,2)
    
    #check if the logged in user is the owner of the listing
    if listing.owner == request.user:
        IsOwner = True
    else: 
        IsOwner = False
    comment_form = CommentForm()
    #if a form is submitted
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        #if the bid form is submitted
        if 'bid' in request.POST:
            # Take in the data the user submitted and save it as form
            form = BidForm(request.POST)
            # Check if form data is valid (server-side)
            if form.is_valid():
                # Isolate the amount from the 'cleaned' version of form data
                amount = form.cleaned_data["amount"]

                #Check if there is any current bids
                if listing.bids.all().count() > 0:
                    #print(f"Bidding on a listing that has {listing.bids.all().count()} bids")
                    #Get the largest current bid
                    current_bid = round(listing.bids.all().aggregate(Max('amount'))['amount__max'],2)
                    # check if amount is greater than current bid
                    if amount > current_bid:
                        bid = form.save(commit=False)
                        bid.listing = listing
                        bid.bidder = request.user
                        bid.save()
                        listing.starting_bid = amount
                        listing.save()
                        print(f'{amount} is greater than current bid {current_bid}, bid accepted')
                        message = "Bid accepted"
                        display_bid = round(amount,2)
                        form = BidForm(initial={'amount':display_bid})
                        form.fields['amount'].widget.attrs['min'] = display_bid


                    else:
                        print(f'{amount} is less than current bid {current_bid}, bid rejected')
                        form.add_error('amount', f'Bid amount must be greater than {current_bid}')
                        message ="Bid Denied"
                        display_bid = round(current_bid,2)
                        

                #No current bids, no one has bid on this item yet
                else:
                    #print(f"Bidding on a listing with 0 bids")
                    #check if amount is greater than starting_bid
                    if amount >= listing.starting_bid:
                        bid = form.save(commit=False)
                        bid.listing = listing
                        bid.bidder = request.user
                        #Saves the form data into a new bid object without committing it to database yet, allowing for further modifications
                        bid.save()
                        listing.starting_bid = amount
                        listing.save()
                        print (f'{amount} is at least as large as starting bid {listing.starting_bid}, bid accepted')
                        message = "Bid accepted"
                        form = BidForm(initial={'amount':display_bid})
                        display_bid = round(amount,2)
                        form.fields['amount'].widget.attrs['min'] = display_bid
                    else:
                        print(f'{amount} is less than starting bid {listing.starting_bid}, bid rejected')
                        form.add_error('amount', f'Bid amount must be at least as large as {listing.starting_bid}')
                        message = "Bid Denied"
                        display_bid = listing.starting_bid

                bid_count = listing.bids.all().count()
                return render(request, "auctions/listing.html",{
                    'form':form,
                    "listing": listing,
                    "onWatchlist": is_watched,
                    "IsOwner": IsOwner,
                    "message": message,
                    "display_bid": display_bid,
                    "bid_count": bid_count,
                    "comment_form": comment_form,
                })
        
            else:
                return render(request, "auctions/listing.html",{
                    "form":form,
                    "listing": listing,
                    "onWatchlist": is_watched,
                    "IsOwner": IsOwner,
                    "message": message,
                    "display_bid": display_bid,
                    "bid_count": bid_count,
                    "comment_form": comment_form,
                })
                
        
        #if the watchlist form is submitted
        elif 'add_watchlist' in request.POST:
            listing.watchlist.add(request.user)
        else:
            listing.watchlist.remove(request.user)
        return HttpResponseRedirect(reverse('listing', args = (listing.id, )))
    
    
    #create the bid form
    bid_form = BidForm(initial={'amount':display_bid})
    #set the minimum value of the bid form to the latest bid value
    bid_form.fields['amount'].widget.attrs['min'] = display_bid
    #Gets a queryset of all comments that belongs to Listing and order by the time stamp in descending order
    comments = listing.comments.all().order_by('-timestamp')
       
    return render(request,"auctions/listing.html",{
        "listing": listing,
        "onWatchlist": is_watched,
        "IsOwner": IsOwner,
        "form":bid_form,
        "display_bid": display_bid,
        "bid_count": bid_count,
        "comment_form": comment_form,
        "comments": comments,
    })

@login_required(login_url='login')
def create(request):
    if request.method == 'POST': #if user submitted the form
        # Take in the data the user submitted and save it as form
        form = CreateListingForm(request.POST)
        #Check if form data is valid (server-side)
        if form.is_valid():
            #Saves the form data into a new 'Listing' object without committing it to database yet, allowing for further modifications
            listing = form.save(commit = False)
            #sets the owner field of the listing to currently logged in user 
            listing.owner = request.user
            listing.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreateListingForm()
    return render(request,"auctions/create.html",{
        "form": form,
    })



def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next')
            if next_url and next_url !='/login':
                modified_next_url = next_url[1:]
                return HttpResponseRedirect(reverse(modified_next_url))
            else:
                return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        print(request.GET.get('next'))
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def watchlist(request):
    #Get the user
    user = User.objects.get(pk=request.user.pk)

    #use the reverse relation to get all the watchlist_listing from this user
    watchlist = user.watchlist_listings.all()
    #get the length of the watchlist
    watchlist_count = user.watchlist_listings.all().count()
    return render(request,"auctions/watchlist.html",{
        "watchlist": watchlist,
        "watchlist_count": watchlist_count,
    })

@login_required(login_url='/login')
def remove_from_watchlist(request, listing_id):
    #Get the Listing whose id matches the id passed in the URL
    listing = get_object_or_404(Listing,pk=listing_id)
    #set user variable to the user logged in
    user = request.user
    #check if the user is authenticated. 
    if user.is_authenticated:
        #check if the user can be found in a queryset of user's watchlist 
        if user in listing.watchlist.all():
            #if true, remove the user 
            listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("watchlist"))

@login_required(login_url='/login')
def bids(request):
    #Get the logged in user object
    user = User.objects.get(pk=request.user.pk)
    #Get all the bids of the user and order by the creation date
    bids = user.bids.all().order_by('-timestamp')
    return render(request,"auctions/bids.html",{
        "bids": bids,
    })

@login_required(login_url='/login')
def close_auction(request, listing_id):
    #Get the logged in user 
    user = request.user
    #Get the listing model instance that matches the id
    listing = Listing.objects.get(id=listing_id)
    #Get a queryset of all the bids of the listing, order it by the amount in descending order,
    #and get the highest bid which is the first item of the list
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

    #if there is any bid: 
    if highest_bid:
        winner= highest_bid.bidder
        print(f"The winner is {winner}")
        #add winner to the listing
        listing.winner = winner
        #deactivate the listing
        listing.is_active = False
        if user.is_authenticated:
            listing.save()
    # If there are 0 bidders and auction needs to be closed
    else:
        print("There is 0 bids and the auction will close now")
        listing.is_active=False
        if user.is_authenticated:
            listing.save()

    return HttpResponseRedirect(reverse('listing', args=(listing.id,)))

@login_required(login_url='/login')
def comment(request,listing_id):
    #when the user submits the form 
    if request.method == "POST":
        #Get the listing that matches the id
        listing = Listing.objects.get(id=listing_id)
        # Take in the data the user submitted and save it as form
        form = CommentForm(request.POST)

        if form.is_valid():
            # Isolate the text from the 'cleaned' version of form data
            text = form.cleaned_data["text"]
            #Saves the form data into a new 'Comment' model object without committing it to database yet, allowing for further modifications
            comment = form.save(commit=False)
            comment.listing = listing
            comment.commenter = request.user
            #save and hit the database
            comment.save()
        
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))        
    else: #GET
        listing = Listing.objects.get(id=listing_id)
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))

def category(request):
    #Get a queryset of all the categories
    categories = Category.objects.all()
    return render(request, "auctions/category.html",{
        'categories': categories,
    })

def category_detail(request, category_id):
    #Get all the listings that belong to a category whose id matches the id, order it by creation date in descending order
    listings = Category.objects.get(id=category_id).listings.all().order_by('-created_at')
    return render(request,"auctions/category_detail.html",{
        "listings":listings,

    })




