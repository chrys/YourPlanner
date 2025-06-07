from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.http import HttpResponseForbidden
from .models import Template, TemplateImage, TemplateService
from .forms import TemplateForm, TemplateImageFormSet, TemplateServiceFormSet
from users.models import Professional


@login_required
def template_list(request):
    """
    Display a list of templates for the logged-in professional.
    """
    try:
        professional = request.user.professional_profile
        templates = Template.objects.filter(professional=professional)
        return render(request, 'template_app/template_list.html', {
            'templates': templates
        })
    except Professional.DoesNotExist:
        messages.error(request, "You need a professional profile to access templates.")
        return redirect('users:profile')


@login_required
def template_detail(request, slug):
    """
    Display details of a specific template.
    """
    template = get_object_or_404(Template, slug=slug)
    
    # Check if the user is the owner of the template
    try:
        if request.user.professional_profile != template.professional:
            return HttpResponseForbidden("You don't have permission to view this template.")
    except Professional.DoesNotExist:
        return HttpResponseForbidden("You need a professional profile to view templates.")
    
    template_services = template.template_services.all().select_related('service')
    template_images = template.images.all()
    
    return render(request, 'template_app/template_detail.html', {
        'template': template,
        'template_services': template_services,
        'template_images': template_images,
    })


@login_required
@transaction.atomic
def template_create(request):
    """
    Create a new template with images and services.
    """
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        messages.error(request, "You need a professional profile to create templates.")
        return redirect('users:profile')
    
    if request.method == 'POST':
        form = TemplateForm(request.POST, professional=professional)
        image_formset = TemplateImageFormSet(request.POST, request.FILES, prefix='images')
        service_formset = TemplateServiceFormSet(request.POST, prefix='services')
        
        # Pass the professional to each service form
        for service_form in service_formset:
            service_form.professional = professional
        
        if form.is_valid() and image_formset.is_valid() and service_formset.is_valid():
            template = form.save()
            
            # Save image formset
            image_formset.instance = template
            image_formset.save()
            
            # Save service formset
            service_formset.instance = template
            service_formset.save()
            
            messages.success(request, f"Template '{template.title}' created successfully.")
            return redirect('template_app:template_detail', slug=template.slug)
    else:
        form = TemplateForm(professional=professional)
        image_formset = TemplateImageFormSet(prefix='images')
        service_formset = TemplateServiceFormSet(prefix='services')
        
        # Pass the professional to each service form
        for service_form in service_formset:
            service_form.professional = professional
    
    return render(request, 'template_app/template_form.html', {
        'form': form,
        'image_formset': image_formset,
        'service_formset': service_formset,
        'is_create': True
    })


@login_required
@transaction.atomic
def template_update(request, slug):
    """
    Update an existing template.
    """
    template = get_object_or_404(Template, slug=slug)
    
    # Check if the user is the owner of the template
    try:
        if request.user.professional_profile != template.professional:
            return HttpResponseForbidden("You don't have permission to edit this template.")
    except Professional.DoesNotExist:
        return HttpResponseForbidden("You need a professional profile to edit templates.")
    
    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template, professional=template.professional)
        image_formset = TemplateImageFormSet(request.POST, request.FILES, instance=template, prefix='images')
        service_formset = TemplateServiceFormSet(request.POST, instance=template, prefix='services')
        
        # Pass the professional to each service form
        for service_form in service_formset:
            service_form.professional = template.professional
        
        if form.is_valid() and image_formset.is_valid() and service_formset.is_valid():
            template = form.save()
            image_formset.save()
            service_formset.save()
            
            messages.success(request, f"Template '{template.title}' updated successfully.")
            return redirect('template_app:template_detail', slug=template.slug)
    else:
        form = TemplateForm(instance=template, professional=template.professional)
        image_formset = TemplateImageFormSet(instance=template, prefix='images')
        service_formset = TemplateServiceFormSet(instance=template, prefix='services')
        
        # Pass the professional to each service form
        for service_form in service_formset:
            service_form.professional = template.professional
    
    return render(request, 'template_app/template_form.html', {
        'form': form,
        'image_formset': image_formset,
        'service_formset': service_formset,
        'template': template,
        'is_create': False
    })


@login_required
def template_delete(request, slug):
    """
    Delete a template.
    """
    template = get_object_or_404(Template, slug=slug)
    
    # Check if the user is the owner of the template
    try:
        if request.user.professional_profile != template.professional:
            return HttpResponseForbidden("You don't have permission to delete this template.")
    except Professional.DoesNotExist:
        return HttpResponseForbidden("You need a professional profile to delete templates.")
    
    if request.method == 'POST':
        template_title = template.title
        template.delete()
        messages.success(request, f"Template '{template_title}' deleted successfully.")
        return redirect('template_app:template_list')
    
    return render(request, 'template_app/template_confirm_delete.html', {
        'template': template
    })

