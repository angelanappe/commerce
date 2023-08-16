from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="createlisting"),
    path("by_category", views.by_category, name="by_category"),
    path("listing/<int:id>", views.listing, name="listing"), # listing/<int:id> means that only who has an id can follow this path
    path("removefromlisting/<int:id>", views.removefromlisting, name="removefromlisting"),
    path("addfromlisting/<int:id>", views.addfromlisting, name="addfromlisting"),
    path("watchlist_list", views.watchlist_list, name="watchlist_list"),
    path("write_a_comment/<int:id>", views.write_a_comment, name="write_a_comment"),
    path("listing_detail/<int:id>", views.listing_detail, name="listing_detail"),
    path('close_auction/<int:id>/', views.close_auction, name='close_auction'),
    path('my_listings/', views.my_listings, name='my_listings'),
    path('won_bids/', views.won_bids, name='won_bids'),
]
