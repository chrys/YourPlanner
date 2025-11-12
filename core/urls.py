from django.urls import path
from .views import home_view, TablesView, LocationsView, LegalView, OurTeamView
from orders.views import SelectItemsView, BasketView

app_name = 'core'  # Define the namespace

urlpatterns = [
    path('', home_view, name='home'),
    # CHANGED: Added /home/ route for post-signup redirect
    path('home/', home_view, name='home_page'),
    # CHANGED: Added pages routes
    path('tables/', TablesView.as_view(), name='tables'),
    path('locations/', LocationsView.as_view(), name='locations'),
    path('legal/', LegalView.as_view(), name='legal'),
    path('our-team/', OurTeamView.as_view(), name='our_team'),
]
