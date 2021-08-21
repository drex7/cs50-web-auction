from django.urls import path, re_path

from . import views

app_name = 'auctions'
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    re_path(r"^listing/(?P<listing_id>\d+)/(?:(.+)/$)", views.listing, name="listing"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>/", views.watchlist, name="watchlist"),
    path("category/", views.category, kwargs={'category_name': None}, name="category"),
    path("category/<str:category_name>/", views.category, name="category"),
    

]

# path("listing/<str:title>/", views.listing, name="listing"),
# re_path(r"^watchlist/$", views.watchlist, name="watchlist"),
