from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import ConfigurationCategory, ConfigurationLabel
from .forms import ConfigurationLabelForm


def is_superuser(user):
    """Check if user is a superuser."""
    return user.is_superuser


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to require superuser access."""
    def test_func(self):
        return self.request.user.is_superuser


class ConfigurationDashboardView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    """
    Dashboard view for configuration management.
    Shows all configuration categories and their labels.
    """
    model = ConfigurationCategory
    template_name = 'configuration/dashboard.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all labels grouped by category
        categories = ConfigurationCategory.objects.all()
        labels_by_category = {}
        
        for category in categories:
            labels_by_category[category] = ConfigurationLabel.objects.filter(category=category)
        
        context['labels_by_category'] = labels_by_category
        return context


class ConfigurationLabelListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    """
    List view for configuration labels.
    """
    model = ConfigurationLabel
    template_name = 'configuration/label_list.html'
    context_object_name = 'labels'

    def get_queryset(self):
        category_name = self.kwargs.get('category')
        if category_name:
            return ConfigurationLabel.objects.filter(category__name=category_name)
        return ConfigurationLabel.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_name = self.kwargs.get('category')
        if category_name:
            context['category'] = get_object_or_404(ConfigurationCategory, name=category_name)
        return context


class ConfigurationLabelCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    """
    Create view for configuration labels.
    """
    model = ConfigurationLabel
    form_class = ConfigurationLabelForm
    template_name = 'configuration/label_form.html'
    success_url = reverse_lazy('configuration:dashboard')

    def get_initial(self):
        initial = super().get_initial()
        category_name = self.kwargs.get('category')
        if category_name:
            category = get_object_or_404(ConfigurationCategory, name=category_name)
            initial['category'] = category
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Label'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Label created successfully.')
        return super().form_valid(form)


class ConfigurationLabelUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    """
    Update view for configuration labels.
    """
    model = ConfigurationLabel
    form_class = ConfigurationLabelForm
    template_name = 'configuration/label_form.html'
    success_url = reverse_lazy('configuration:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Label'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Label updated successfully.')
        return super().form_valid(form)


class ConfigurationLabelDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    """
    Delete view for configuration labels.
    """
    model = ConfigurationLabel
    template_name = 'configuration/label_confirm_delete.html'
    success_url = reverse_lazy('configuration:dashboard')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Label deleted successfully.')
        return super().delete(request, *args, **kwargs)

