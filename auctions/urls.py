from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("create",views.create, name="create"),
    path("watchlist",views.watchlist, name="watchlist"),
    path("bids", views.bids, name="bids"),
    path("unwatch/<int:listing_id>", views.remove_from_watchlist, name = "unwatch"),
    path("close_auction/<int:listing_id>", views.close_auction,name="close_auction"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("category", views.category, name="category" ),
    path("category_detail/<int:category_id>", views.category_detail, name="category_detail"),
]
