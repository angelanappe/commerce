from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    the_category = models.CharField(max_length=100)

    def __str__(self):
        # Display the category name: suspense, romance, etc..
        return self.the_category

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=400)
    url_image = models.CharField(max_length=1000)
    price = models.FloatField()
    activation_status = models.BooleanField(default=True)
    # .CASCADE = if you delete the owner it deletes everything that has to do with him/her
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist")
    winning_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="winning_listings")

    def __str__(self):
        # Display what i'm offering using its title
        return self.title
    
class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="author_comment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_comment")
    message = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"
    
class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="offer_user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_offer")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)