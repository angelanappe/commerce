from django.contrib import admin
from .models import User, Category, Listing, Comments, Offer

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comments)
admin.site.register(Offer)