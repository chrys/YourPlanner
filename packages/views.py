from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView, TemplateView
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Template, TemplateItemGroup, TemplateItemGroupItem
from .forms import TemplateForm, TemplateImageFormSet, TemplateItemGroupFormSet
from orders.models import Order
from users.models import Professional

try:
    from users.mixins import ProfessionalRequiredMixin
except ImportError:
    try:
        from core.mixins import ProfessionalRequiredMixin
    except ImportError:
        from django.contrib.auth.mixins import AccessMixin
        class ProfessionalRequiredMixin(AccessMixin):
            def test_func(self):
                try:
                    return hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None
                except Professional.DoesNotExist:
                    return False

            def handle_no_permission(self):
                messages.error(self.request, "You are not registered as a professional.")
                return redirect('users:user_management')  # CHANGED: Fixed from 'profile_choice' to 'user_management'

class TemplateDeleteView(LoginRequiredMixin, ProfessionalRequiredMixin, DeleteView):  # New delete view
    """
    Delete view for Template with order usage check.
    Prevents deletion if template is used in any customer orders.
    """
    model = Template
    template_name = 'templates/template_confirm_delete.html'  # confirmation template
    success_url = reverse_lazy('packages:template-list')  # redirect after deletion
    context_object_name = 'template'

    def get_queryset(self):  # Ensure professional owns the template
        return Template.objects.filter(professional=self.request.user.professional_profile)

    def get_context_data(self, **kwargs):  # Check for orders using this template
        context = super().get_context_data(**kwargs)
        template = self.get_object()
        
        # Find all orders using this template
        orders_using_template = Order.objects.filter(template=template).select_related('customer__user')
        context['orders_using_template'] = orders_using_template
        context['page_title'] = f"Delete Package: {template.title}"
        
        return context

    def delete(self, request, *args, **kwargs):  # Override to check for orders before deletion
        template = self.get_object()
        
        # Check if template is used in any orders
        orders_count = Order.objects.filter(template=template).count()
        if orders_count > 0:
            messages.error(
                request,
                f"Cannot delete package '{template.title}' because it is used in {orders_count} customer order(s). "
                "Please cancel or complete these orders first."
            )
            return self.get(request, *args, **kwargs)
        
        # Proceed with deletion if no orders use this template
        messages.success(request, f"Package '{template.title}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


class TemplateCreateView(LoginRequiredMixin, ProfessionalRequiredMixin, CreateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates/template_form.html'
    success_url = reverse_lazy('packages:template-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        professional_profile = None
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            professional_profile = self.request.user.professional_profile

        dummy_template_instance = None
        if professional_profile:
            dummy_template_instance = Template(professional=professional_profile)

        if self.request.POST:
            instance_for_formset = self.object if self.object and self.object.pk else dummy_template_instance
            data['image_formset'] = TemplateImageFormSet(self.request.POST, self.request.FILES, instance=instance_for_formset, prefix='images')
            # Handle item group formset
            num_groups = int(self.request.POST.get('number_of_groups', 0))
            data['group_formset'] = TemplateItemGroupFormSet(
                self.request.POST,
                instance=instance_for_formset,
                prefix='groups',
                form_kwargs={'professional': professional_profile}
            )
            data['number_of_groups'] = num_groups
        else:
            data['image_formset'] = TemplateImageFormSet(instance=dummy_template_instance, prefix='images')
            # Initialize empty group formset for create
            data['group_formset'] = TemplateItemGroupFormSet(
                instance=dummy_template_instance,
                prefix='groups',
                form_kwargs={'professional': professional_profile}
            )
            data['number_of_groups'] = 0

        # Provide all_items for dynamic group JS
        from services.models import Item
        if professional_profile:
            all_items = Item.objects.filter(service__professional=professional_profile, is_active=True).select_related('service').order_by('service__title', 'title')
        else:
            all_items = Item.objects.none()
        data['all_items'] = all_items
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        group_formset = context['group_formset']

        default_image_count = 0
        has_at_least_one_image_to_upload = False

        if not form.is_valid():
            return self.form_invalid(form)

        # Validate image formset
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

        # Validate group formset
        if not group_formset.is_valid():
            for error_list in group_formset.non_form_errors():
                for error in error_list:
                    form.add_error(None, error)
            for i_form_idx, errors_dict in enumerate(group_formset.errors):
                if errors_dict:
                    for field, field_errors in errors_dict.items():
                        for e in field_errors:
                            form.add_error(None, _("Group %(num)d (%(field)s): %(error)s") % {'num': i_form_idx + 1, 'field': field, 'error': e})
            return self.form_invalid(form)

        # Validate images
        for image_data in image_formset.cleaned_data:
            if image_data and not image_data.get('DELETE', False):
                if image_data.get('image'):
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

        with transaction.atomic():  # Use atomic transaction for data consistency
            try:
                if not (hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None):
                    messages.error(self.request, _("Professional profile not found for this user."))
                    form.add_error(None, _("Professional profile not found."))
                    return self.form_invalid(form)

                self.object = form.save(commit=False)
                self.object.professional = self.request.user.professional_profile
                self.object.save()
                form.save_m2m()

                # Save image formset
                image_formset.instance = self.object
                image_formset.save()

                if has_at_least_one_image_to_upload and not self.object.images.filter(is_default=True).exists():
                    first_image = self.object.images.first()
                    if first_image:
                        first_image.is_default = True
                        first_image.save()
                        messages.info(self.request, _("The first uploaded image has been set as default."))

                # Save item groups and their items
                group_formset.instance = self.object
                saved_groups = group_formset.save(commit=False)
                
                for group in saved_groups:
                    group.save()
                    
                    # Get the items selected for this group from formset
                    group_form = None
                    for form_instance in group_formset.forms:
                        if form_instance.instance == group:
                            group_form = form_instance
                            break
                    
                    # Create item group items using objects.create() to properly handle auto_now fields
                    if group_form and 'items' in group_form.cleaned_data:
                        selected_items = group_form.cleaned_data['items']
                        
                        # Clear existing items before adding new ones
                        TemplateItemGroupItem.objects.filter(group=group).delete()
                        
                        # Create items individually to properly trigger auto_now field updates
                        for position, item in enumerate(selected_items):
                            TemplateItemGroupItem.objects.create(
                                group=group,
                                item=item,
                                position=position
                            )
                
                # Handle deleted groups
                for deleted_group in group_formset.deleted_objects:
                    deleted_group.delete()

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
        return kwargs


class TemplateUpdateView(LoginRequiredMixin, ProfessionalRequiredMixin, UpdateView):
    model = Template
    form_class = TemplateForm
    template_name = 'templates/template_form.html'
    context_object_name = 'template'

    def get_success_url(self):
        return reverse_lazy('packages:template-detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            return Template.objects.filter(professional=self.request.user.professional_profile)
        return Template.objects.none()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        professional_profile = None
        if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            professional_profile = self.request.user.professional_profile

        if self.request.POST:
            data['image_formset'] = TemplateImageFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='images')
            # Handle item group formset for update
            num_groups = int(self.request.POST.get('number_of_groups', 0))
            data['group_formset'] = TemplateItemGroupFormSet(
                self.request.POST,
                instance=self.object,
                prefix='groups',
                form_kwargs={'professional': professional_profile}
            )
            data['number_of_groups'] = num_groups
        else:
            data['image_formset'] = TemplateImageFormSet(instance=self.object, prefix='images')
            # Load existing groups for editing
            data['group_formset'] = TemplateItemGroupFormSet(
                instance=self.object,
                prefix='groups',
                form_kwargs={'professional': professional_profile}
            )
            data['number_of_groups'] = self.object.item_groups.count()

        # Provide all_items for dynamic group JS
        from services.models import Item
        if professional_profile:
            all_items = Item.objects.filter(service__professional=professional_profile, is_active=True).select_related('service').order_by('service__title', 'title')
        else:
            all_items = Item.objects.none()
        data['all_items'] = all_items
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        group_formset = context['group_formset']

        default_image_count = 0
        has_at_least_one_image_to_upload = False

        if not form.is_valid():
            return self.form_invalid(form)

        # Validate image formset
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

        # Validate group formset
        if not group_formset.is_valid():
            for error_list in group_formset.non_form_errors():
                for error in error_list:
                    form.add_error(None, error)
            for i_form_idx, errors_dict in enumerate(group_formset.errors):
                if errors_dict:
                    for field, field_errors in errors_dict.items():
                        for e in field_errors:
                            form.add_error(None, _("Group %(num)d (%(field)s): %(error)s") % {'num': i_form_idx + 1, 'field': field, 'error': e})
            return self.form_invalid(form)

        # Validate images
        for image_data in image_formset.cleaned_data:
            if image_data and not image_data.get('DELETE', False):
                if image_data.get('image'):
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

        with transaction.atomic():  # Use atomic transaction for data consistency
            try:
                if not (hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None):
                    messages.error(self.request, _("Professional profile not found for this user."))
                    form.add_error(None, _("Professional profile not found."))
                    return self.form_invalid(form)

                self.object = form.save(commit=False)
                self.object.professional = self.request.user.professional_profile
                self.object.save()
                form.save_m2m()

                # Save image formset
                image_formset.instance = self.object
                image_formset.save()

                if has_at_least_one_image_to_upload and not self.object.images.filter(is_default=True).exists():
                    first_image = self.object.images.first()
                    if first_image:
                        first_image.is_default = True
                        first_image.save()
                        messages.info(self.request, _("The first uploaded image has been set as default."))

                # Save item groups and their items
                group_formset.instance = self.object
                saved_groups = group_formset.save(commit=False)
                
                for group in saved_groups:
                    group.save()
                    
                    # Get the items selected for this group from formset
                    group_form = None
                    for form_instance in group_formset.forms:
                        if form_instance.instance == group:
                            group_form = form_instance
                            break
                    
                    # Create item group items using objects.create() to properly handle auto_now fields
                    if group_form and 'items' in group_form.cleaned_data:
                        selected_items = group_form.cleaned_data['items']
                        
                        # Clear existing items before adding new ones
                        TemplateItemGroupItem.objects.filter(group=group).delete()
                        
                        # Create items individually to properly trigger auto_now field updates
                        for position, item in enumerate(selected_items):
                            TemplateItemGroupItem.objects.create(
                                group=group,
                                item=item,
                                position=position
                            )
                
                # Handle deleted groups
                for deleted_group in group_formset.deleted_objects:
                    deleted_group.delete()

            except Professional.DoesNotExist:
                messages.error(self.request, _("User is not associated with a professional profile."))
                form.add_error(None, _("User is not a professional."))
                return self.form_invalid(form)
            except Exception as e:
                messages.error(self.request, _("An unexpected error occurred: %(error)s") % {'error': str(e)})
                form.add_error(None, _("An unexpected error occurred during saving."))
                return self.form_invalid(form)

        messages.success(self.request, _("Template updated successfully!"))
        return super().form_valid(form)


class TemplateListView(LoginRequiredMixin, ProfessionalRequiredMixin, ListView):
    model = Template
    context_object_name = 'templates'
    template_name = 'templates/template_list.html'

    def get_queryset(self):
        try:
            if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
                professional = self.request.user.professional_profile
                return Template.objects.filter(professional=professional).prefetch_related('images', 'services').order_by('-updated_at')
            else:
                messages.error(self.request, _("User profile is not configured as a professional."))
                return Template.objects.none()
        except Professional.DoesNotExist:
            messages.error(self.request, _("You are not registered as a professional."))
            return Template.objects.none()
        except AttributeError:
             messages.error(self.request, _("Could not identify your professional profile attribute."))
             return Template.objects.none()


class TemplateDetailView(LoginRequiredMixin, DetailView):
    model = Template
    template_name = 'templates/template_detail.html'
    context_object_name = 'template'

    def get_queryset(self):
        # Added item_groups prefetch for related items
        qs = Template.objects.prefetch_related('images', 'services__category', 'item_groups__items__item')
        if self.request.user.is_superuser:
            return qs

        try:
            if hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
                 return qs.filter(professional=self.request.user.professional_profile)
            return Template.objects.none()
        except Professional.DoesNotExist:
             return Template.objects.none()
        except AttributeError:
            return Template.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.object

        context['default_image'] = template.images.filter(is_default=True).first()
        context['other_images'] = template.images.filter(is_default=False)

        # Add item groups to context
        context['item_groups'] = template.item_groups.prefetch_related('items__item__service').order_by('position', 'name')

        is_owner_or_superuser = False
        if self.request.user.is_superuser:
            is_owner_or_superuser = True
        elif hasattr(self.request.user, 'professional_profile') and self.request.user.professional_profile is not None:
            if template.professional == self.request.user.professional_profile:
                is_owner_or_superuser = True

        context['is_owner_or_superuser'] = is_owner_or_superuser

        return context


# CHANGED: Added PackagesView for displaying wedding packages
class PackagesView(TemplateView):
    """
    View to display wedding packages.
    """
    # CHANGED: Corrected template path to match packages/templates/templates/ structure
    template_name = 'templates/packages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Wedding Packages"
        return context
