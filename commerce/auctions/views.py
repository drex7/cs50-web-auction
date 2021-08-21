from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import F, Exists, OuterRef

from decimal import Decimal

from .models import *


# Templates
INDEX_TEMPLATE = "auctions/index.html"
LISTING_TEMPLATE = "auctions/listing.html"
REGISTER_TEMPLATE = "auctions/register.html"

def index(request):
    context = {
        'listings': Listing.objects.order_by('-active'),
    }
    if request.user.is_authenticated:
        listings = Listing.objects.annotate(
            is_on_watchlist=Exists(Watchlist.objects.filter(listing=OuterRef('pk'), user=request.user))
            ).order_by('-active')
        context['listings'] = listings
    return render(request, INDEX_TEMPLATE, context=context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print(request.user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, REGISTER_TEMPLATE, {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, REGISTER_TEMPLATE, {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, REGISTER_TEMPLATE)


@login_required
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            Listing.objects.create(
                created_by = request.user,
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                starting_bid = form.cleaned_data['starting_bid'],
                category = form.cleaned_data['category'],
                image_url = form.cleaned_data['image_url']
                )

            return HttpResponseRedirect(reverse('auctions:index'))
    else:
        form = NewListingForm()

    return render(request, "auctions/create_listing.html", {
        'new_listing': form,
    })


def listing(request, listing_id): 
    listing = Listing.objects.get(id=listing_id)

    comments = listing.comments.order_by('-time').annotate(username=F('commentor__username'))
    
    # Get highest bid
    highest_bid = listing.bids.order_by('-amount')
    if highest_bid:
        highest_bidder = highest_bid[0].bidder.username
        highest_bid = highest_bid[0].amount
    else:
        highest_bid = listing.starting_bid
        highest_bidder = None

    context = { 
        'listing': listing,
        'bid_form': BiddingForm,
        'comment_form': CommentForm,        
        'comments': comments,
        'highest_bidder': highest_bidder,
        'highest_bid': highest_bid,
    }

    user = request.user
    if user.is_authenticated:
        # Check if listing is on watchlist
        listing_watchlist_count = listing.watchlist.filter(user=user).count()
        context['is_on_watchlist'] = True if listing_watchlist_count > 0 else False
    if request.method == "POST":

        # Check if listing is on watchlist
        
        action = request.POST['action']

        # A comment is being submitted
        if action == "comment":
            listing.comments.create(
                commentor=user,
                content=request.POST['content']
            )    
            return HttpResponseRedirect(reverse('auctions:listing', args=[listing_id, listing.title]))

        # Close the bidding
        elif action == "close":   
            # Close the bid, and get the highest bidder
            listing.active = "False"
            listing.save()  
            return HttpResponseRedirect(reverse('auctions:listing', args=[listing_id, listing.title]))

        else:  
            # A bid is being placed
            # Receive the form data about the bid
            form = BidForm(request.POST)
            amount = request.POST['amount']    
            if amount: 
                submitted_bid = Decimal(amount) 
                
                if highest_bid:
                    
                    if submitted_bid > highest_bid:
                        # listing already has bids on it
                        listing.bids.create(
                            bidder_id=user.id, 
                            amount=submitted_bid
                        )
                        context['highest_bid'] = submitted_bid
                        context['form_validity'] = "is-valid"
                        return HttpResponseRedirect(reverse('auctions:listing', args=[listing_id, listing.title]))
                    else:
                        # submitted_bid is less than current highest bid
                        context['form_validity'] = "is-invalid"
                        return HttpResponseRedirect(reverse('auctions:listing', args=[listing_id, listing.title]))
                        
                else:
                    # Listing has no bids yet
                    listing.bids.create(
                        bidder_id=user.id, 
                        amount=submitted_bid
                    )
                    context['form-validity'] = "is-valid"
                    context['highest_bid'] = submitted_bid
                
                    # context['listing'] = Bid.objects.filter(listing_id=listing_id).order_by('-amount')[0]
                    return HttpResponseRedirect(reverse('auctions:listing', args=[listing_id, listing.title]))

            else:   
                # form is not valid
                # Return form with submitted values
                context['bid_form'] = form
                return render(request, LISTING_TEMPLATE, context=context)
 
    # Request is GET
    else:   
        return render(request, LISTING_TEMPLATE,
        context=context)


@login_required
def watchlist(request, listing_id=None):
    
    user = request.user
    watchlist = Watchlist.objects.filter(user=user)

    watchlist = Listing.objects.filter(
        id__in=watchlist.values('listing_id')).annotate(
            is_on_watchlist=Exists(watchlist)
        )    
    if request.method == "POST":
        action = request.POST["action"]
        
        if action == "add":
            # Add listing to watchlist
            user.user_watchlist.create(listing_id=listing_id)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:   
            # Remove listing from watchlist
            Watchlist.objects.filter(user=user, listing_id=listing_id).delete()
            return HttpResponseRedirect(reverse("auctions:index"))
   
    else:   # Request is get
        return render(request, "auctions/watchlist.html", {
            'watchlist': watchlist,
        })
    

def category(request, category_name):
    CATEGORIES = Listing.category.field.choices
    categories = [item[1] for item in CATEGORIES]
    categories.insert(0, 'All')

    context = {
            'listings_by_category': Listing.objects.filter(category__iexact=category_name).order_by('-active'), 
            'categories': categories,
            }
    
    if category_name == 'All':
        context['listings_by_category'] = Listing.objects.order_by('-active')     

    return render(request, "auctions/category.html",
        context=context
    )


class BidForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    listing_id = forms.IntegerField(max_value=150, min_value=0)
    