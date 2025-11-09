from django.shortcuts import render, redirect

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