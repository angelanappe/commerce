from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Comments, Offer


def index(request):
    active_status = Listing.objects.filter(activation_status=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": active_status,
        "categories": categories
    })

def by_category(request):
    if request.method == "POST":
        category = Category.objects.get(the_category=request.POST["category"])
        active_status = Listing.objects.filter(activation_status=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": active_status,
            "categories": categories
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
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
    

def create_listing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/createlisting.html", {
            "categories": categories
        })
    else:
        # get data from form, then create new listing object, then insert object in db and redirect to index page
        title = request.POST["title"]
        description = request.POST["description"]
        url_image = request.POST["url_image"]
        price = request.POST["price"]
        category = request.POST["category"]
        # get the user using request.user
        logged_user = request.user

        # Get everything about contents, of specific category
        category_contents = Category.objects.get(the_category=category)
        # create object of new listing
        new = Listing(
            title=title,
            description=description,
            url_image=url_image,
            price=float(price),
            category=category_contents,
            owner=logged_user
        )
        # insert object in db
        new.save()
        return HttpResponseRedirect(reverse(index))
    

def listing(request, id):
    listinginfo = Listing.objects.get(pk=id)
    listing_in_watchlist = request.user in listinginfo.watchlist.all() # Checking if user is on this listing
    listing_comments = Comments.objects.filter(listing=listinginfo)
    return render(request, "auctions/listing.html", {
        "listing" : listinginfo,
        "listing_in_watchlist": listing_in_watchlist,
        "listing_comments": listing_comments
    })


def removefromlisting(request, id):
    listinginfo = Listing.objects.get(pk=id) # Get all contents on Listing
    user = request.user # Current user
    listinginfo.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def addfromlisting(request, id):
    listinginfo = Listing.objects.get(pk=id) # Get all contents on Listing
    user = request.user # Current user
    listinginfo.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def watchlist_list(request):
    user = request.user
    listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings" : listings
    })


def write_a_comment(request, id):
    user = request.user
    listinginfo = Listing.objects.get(pk=id)
    message = request.POST['write_a_comment']

    addcomment = Comments(
        author = user,
        listing=listinginfo,
        message=message
    )
    addcomment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))


def listing_detail(request, id):
    listing = get_object_or_404(Listing, pk=id)
    
    if request.method == 'POST':
        bid_amount = float(request.POST['bid_amount'])
        highest_bid = listing.listing_offer.latest('amount').amount if listing.listing_offer.exists() else listing.price

        if bid_amount >= highest_bid:
            bid = Offer(user=request.user, listing=listing, amount=bid_amount)
            bid.save()
            messages.success(request, 'Your bid has been placed!')
            return redirect('listing_detail', id=id)
        else:
            messages.error(request, 'Invalid bid. Please check your bid amount.')
    
    return render(request, 'auctions/listing_detail.html', {
        "listing": listing
    })


def close_auction(request, id):
    listing = get_object_or_404(Listing, pk=id, owner=request.user, activation_status=True)

    if request.method == 'POST':
        highest_bid = listing.listing_offer.aggregate(Max('amount'))['amount__max']

        if highest_bid is not None:
            winning_bid = listing.listing_offer.filter(amount=highest_bid).first()
            listing.winning_user = winning_bid.user
            listing.activation_status = False
            listing.save()

            return render(request, 'auctions/auction_closed.html', {
                'listing': listing,
                'winning_bid': winning_bid,
            })

    return HttpResponseRedirect(reverse('listing_detail', args=(id,)))


@login_required
def my_listings(request):
    owned_listings = Listing.objects.filter(owner=request.user)
    return render(request, 'auctions/my_listings.html', {
        'owned_listings': owned_listings
        })


@login_required
def won_bids(request):
    won_listings = Listing.objects.filter(winning_user=request.user)
    bids_made = Offer.objects.filter(listing__in=won_listings).order_by('-amount')
    return render(request, 'auctions/won_bids.html', {
        'won_listings': won_listings,
        'bids_made': bids_made
    })
