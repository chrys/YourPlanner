from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# CHANGED: Updated home_view to redirect authenticated vs unauthenticated users
def home_view(request):
    """
    Main entry point for the application.
    CHANGED: Redirects unauthenticated users to login, authenticated users see home dashboard.
    """
    if not request.user.is_authenticated:
        # CHANGED: Redirect unauthenticated users to login page
        return redirect('users:login')
    
        # CHANGED: Authenticated users see the home dashboard page
    return render(request, 'core/home.html')


# CHANGED: Added TablesView for displaying table and floor plans
class TablesView(TemplateView):
    """
    View to display table and floor plans.
    """
    template_name = 'core/tables.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Table & Floor Plans"
        return context


# CHANGED: Added LocationsView for displaying event locations
class LocationsView(TemplateView):
    """
    View to display event locations.
    """
    template_name = 'core/locations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Event Locations"
        return context


# CHANGED: Added LegalView for displaying legal and documents
class LegalView(TemplateView):
    """
    View to display legal and documents.
    """
    template_name = 'core/legal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Legal & Documents"
        return context


# CHANGED: Added OurTeamView for displaying team information
class OurTeamView(TemplateView):
    """
    View to display team information.
    """
    template_name = 'core/our_team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Our Team"
        return context
