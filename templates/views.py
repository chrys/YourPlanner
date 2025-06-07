from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView # Add DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Template
from .forms import TemplateForm, TemplateImageFormSet
from users.models import Professional # Ensure this path is correct

# Attempt to import a common ProfessionalRequiredMixin
# This is a placeholder, actual location might vary.
# If not found, the basic version below will be used.
try:
    from users.mixins import ProfessionalRequiredMixin # Common location
except ImportError:
    try:
        from core.mixins import ProfessionalRequiredMixin # Another common location
    except ImportError:
        # Basic ProfessionalRequiredMixin if not found elsewhere
        from django.contrib.auth.mixins import AccessMixin
        class ProfessionalRequiredMixin(AccessMixin):
            def dispatch(self, request, *args, **kwargs):
                if not request.user.is_authenticated:
                    return self.handle_no_permission()
                # Check if the user has a professional profile or is a superuser
                # The check for professional_profile should be specific to your User model structure
                # Assuming Professional model has a OneToOneField to User named 'user'
                # and User model has a related name 'professional_profile'
                is_professional = hasattr(request.user, 'professional_profile') and request.user.professional_profile is not None

                if not (is_professional or request.user.is_superuser):
                    messages.error(request, _("You do not have permission to access this page."))
                    return redirect('core:home') # Redirect to home or a relevant error page
                return super().dispatch(request, *args, **kwargs)


class TemplateCreateView(LoginRequiredMixin, ProfessionalRequiredMixin, CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates/template_form.html' # To be created in a later step
    success_url = reverse_lazy('templates:template-list') # Assuming a list view will be created

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        professional_profile = None
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            professional_profile = self.request.user.professional_profile

        # Create a dummy Template instance if professional_profile is available
        # This is necessary for the inline formset if the main object (Template) is not yet saved.
        dummy_template_instance = None
        if professional_profile:
            # Pass only the professional instance, other fields can be blank or default
            dummy_template_instance = Template(professional=professional_profile)


        if self.request.POST:
            # Pass the unsaved object to the formset if it's a new template
            # If editing, self.object will be the template instance
            instance_for_formset = self.object if self.object and self.object.pk else dummy_template_instance
            data['image_formset'] = TemplateImageFormSet(self.request.POST, self.request.FILES, instance=instance_for_formset, prefix='images')
        else:
            data['image_formset'] = TemplateImageFormSet(instance=dummy_template_instance, prefix='images') # Pass dummy for new template
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        default_image_count = 0
        has_at_least_one_image_to_upload = False

        # Validate the main form first
        if not form.is_valid():
            # If image_formset processing is needed even if form is invalid, adjust this.
            # But typically, if main form is invalid, no point proceeding.
            return self.form_invalid(form)

        # Now, validate the formset. This populates cleaned_data for valid forms.
        if not image_formset.is_valid():
            # Add formset non-form errors (if any) to the main form
            for error_list in image_formset.non_form_errors():
                 for error in error_list: # error_list is a list of error strings
                    form.add_error(None, error) # Add to non-field errors of the main form
            # Add errors from individual image forms to the main form
            for i_form_idx, errors_dict in enumerate(image_formset.errors): # errors is a list of dicts
                if errors_dict: # If there are errors for this specific form
                    for field, field_errors in errors_dict.items():
                        for e in field_errors:
                            form.add_error(None, _("Image %(num)d (%(field)s): %(error)s") % {'num': i_form_idx + 1, 'field': field, 'error': e})
            return self.form_invalid(form) # Return after collecting all formset errors

        # Iterate through cleaned_data which contains data for valid forms only
        # image_formset.cleaned_data is a list of dictionaries
        for image_data in image_formset.cleaned_data:
            if image_data and not image_data.get('DELETE', False): # Ensure data exists and not marked for deletion
                if image_data.get('image'): # Check if an image is actually being uploaded
                    has_at_least_one_image_to_upload = True
                if image_data.get('is_default', False):
                    default_image_count += 1

        if has_at_least_one_image_to_upload:
            if default_image_count == 0:
                form.add_error(None, _("If you upload images, you must select one image as the default."))
                return self.form_invalid(form)
            elif default_image_count > 1:
                form.add_error(None, _("Only one image can be marked as default."))
                return self.form_invalid(form)

        # All validations passed, proceed with saving
        with transaction.atomic():
            try:
                if not (hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None):
                    messages.error(self.request, _("Professional profile not found for this user."))
                    form.add_error(None, _("Professional profile not found."))
                    return self.form_invalid(form)

                self.object = form.save(commit=False)
                self.object.professional = self.request.user.professional_profile
                self.object.save()
                form.save_m2m()

                image_formset.instance = self.object
                image_formset.save()

                # Fallback: if after saving everything, there are images but none is default (should be caught by earlier checks)
                if has_at_least_one_image_to_upload and not self.object.images.filter(is_default=True).exists():
                     first_image = self.object.images.first()
                     if first_image:
                         first_image.is_default = True
                         first_image.save()
                         messages.info(self.request, _("The first uploaded image has been set as default as no default was explicitly chosen."))


            except Professional.DoesNotExist:
                messages.error(self.request, _("User is not associated with a professional profile."))
                form.add_error(None, _("User is not a professional."))
                return self.form_invalid(form)
            except Exception as e:
                messages.error(self.request, _("An unexpected error occurred: %(error)s") % {'error': str(e)})
                form.add_error(None, _("An unexpected error occurred during saving."))
                return self.form_invalid(form)

        messages.success(self.request, _("Template created successfully!"))
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Example: Pass professional to form if needed for filtering services based on professional
        # if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
        #     kwargs['professional'] = self.request.user.professional_profile
        return kwargs


class TemplateUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates/template_form.html' # Same form template can be used
    context_object_name = 'template' # To refer to the template instance in the template

    def get_success_url(self):
        # Redirect to the detail view of the updated template
        return reverse_lazy('templates:template-detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        # Ensure professionals can only update their own templates
        # Make sure professional_profile exists and is not None
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            return Template.objects.filter(professional=self.request.user.professional_profile)
        # Return an empty queryset if no professional profile, effectively denying access
        # This should ideally be caught by ProfessionalRequiredMixin, but as a safeguard:
        return Template.objects.none()


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['image_formset'] = TemplateImageFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='images')
        else:
            data['image_formset'] = TemplateImageFormSet(instance=self.object, prefix='images')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        default_image_count = 0
        has_at_least_one_image_being_saved = False # Includes new and existing non-deleted images

        # Validate the main form first
        if not form.is_valid():
            return self.form_invalid(form)

        # Now, validate the formset.
        if not image_formset.is_valid():
            for error_list in image_formset.non_form_errors():
                for error in error_list:
                    form.add_error(None, error)
            for i_form_idx, errors_dict in enumerate(image_formset.errors):
                if errors_dict:
                    for field, field_errors in errors_dict.items():
                        for e in field_errors:
                            form.add_error(None, _("Image %(num)d (%(field)s): %(error)s") % {'num': i_form_idx + 1, 'field': field, 'error': e})
            return self.form_invalid(form)

        # Iterate over cleaned_data from the formset
        for image_data in image_formset.cleaned_data:
            if image_data: # Ensure dictionary is not empty
                if image_data.get('DELETE'):
                    # If an image marked for deletion was default, this needs careful handling.
                    # The save() method of TemplateImage model already handles unsetting other defaults
                    # if a new one is set. If a default is deleted, logic below will set a new one.
                    continue

                # An image is considered "being saved" if it's present (new or existing and not deleted)
                if image_data.get('image') or image_data.get('id'):
                    has_at_least_one_image_being_saved = True

                if image_data.get('is_default', False):
                    default_image_count += 1

        if has_at_least_one_image_being_saved:
            if default_image_count == 0:
                form.add_error(None, _("If you have images for the template, you must select one as the default."))
                return self.form_invalid(form)
            elif default_image_count > 1:
                form.add_error(None, _("Only one image can be marked as default."))
                return self.form_invalid(form)

        # If all images are marked for deletion, has_at_least_one_image_being_saved will be False,
        # and the default_image_count checks above will be skipped, which is correct.

        with transaction.atomic():
            self.object = form.save()

            image_formset.instance = self.object
            image_formset.save()

            # Auto-set default if needed after all operations
            # This covers cases where the default image was deleted, or no default was set with existing/new images.
            if not self.object.images.filter(is_default=True).exists() and self.object.images.exists():
                first_image = self.object.images.order_by('created_at').first() # or some other deterministic order
                if first_image:
                    first_image.is_default = True
                    first_image.save(update_fields=['is_default'])
                    messages.info(self.request, _("The default image was automatically set to the oldest image, as the previous one was removed or none was chosen."))

        messages.success(self.request, _("Template updated successfully!"))
        return redirect(self.get_success_url())


class TemplateListView(LoginRequiredMixin, ProfessionalRequiredMixin, ListView):
    model = Template
    context_object_name = 'templates'
    template_name = 'templates/template_list.html' # To be created

    def get_queryset(self):
        # Professionals should only see their own templates
        try:
            # Ensure professional_profile exists and is not None
            if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
                professional = self.request.user.professional_profile
                return Template.objects.filter(professional=professional).prefetch_related('images', 'services').order_by('-updated_at')
            else: # No professional profile linked to the user
                messages.error(self.request, _("User profile is not configured as a professional."))
                return Template.objects.none()
        except Professional.DoesNotExist: # Should be caught by hasattr check ideally
            messages.error(self.request, _("You are not registered as a professional."))
            return Template.objects.none()
        except AttributeError: # If user object for some reason doesn't have professional_profile
             messages.error(self.request, _("Could not identify your professional profile attribute."))
             return Template.objects.none()


class TemplateDetailView(LoginRequiredMixin, DetailView): # ProfessionalRequiredMixin could be added if only pros can see details
    model = Template
    context_object_name = 'template'
    template_name = 'templates/template_detail.html' # To be created

    def get_queryset(self):
        # Allow viewing if user is the professional who owns it OR if it's part of a public/shared context (not defined yet, so restrict to owner for now)
        # For now, only the professional who owns the template can view its detail page.
        # Superusers can view any.
        qs = Template.objects.prefetch_related('images', 'services__category') # Added prefetch for services and their categories
        if self.request.user.is_superuser:
            return qs

        # Check for professional profile for non-superusers
        try:
            if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
                 return qs.filter(professional=self.request.user.professional_profile)
            # If no professional_profile, they cannot see any templates unless they are a superuser (handled above)
            return Template.objects.none()
        except Professional.DoesNotExist: # Should be rare given hasattr
             return Template.objects.none()
        except AttributeError: # In case professional_profile attribute doesn't exist on user
            return Template.objects.none()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.object # self.object is the Template instance fetched by DetailView

        # Get default image
        context['default_image'] = template.images.filter(is_default=True).first()

        # Get other images (excluding default)
        context['other_images'] = template.images.filter(is_default=False)

        # For Professionals viewing their own template, add a flag for edit/delete buttons
        # Also allow superusers to see these controls, assuming they might need to manage templates
        is_owner_or_superuser = False
        if self.request.user.is_superuser:
            is_owner_or_superuser = True
        elif hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            if template.professional == self.request.user.professional_profile:
                is_owner_or_superuser = True

        context['is_owner_or_superuser'] = is_owner_or_superuser

        return context
