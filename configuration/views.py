from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from labels.models import Label, LABEL_TYPES
from .forms import LabelForm
from django.http import HttpResponseNotAllowed


@staff_member_required
def configuration_index(request):
    """
    Renders the main configuration page.
    """
    # Filter out 'custom' for direct links if it's meant to be accessed differently,
    # or include all if 'custom' also has a dedicated management page like others.
    # For now, let's list all standard types.
    label_types_for_view = [lt for lt in LABEL_TYPES] # List all types
    return render(request, 'configuration/index.html', {'label_types': label_types_for_view})

@staff_member_required
def manage_labels(request, label_type):
    """
    Manages labels for a specific type (section).
    Handles creation of new labels and listing existing ones.
    """
    valid_label_types = [lt[0] for lt in LABEL_TYPES]
    if label_type not in valid_label_types:
        messages.error(request, f"Invalid label type: {label_type}")
        return redirect('configuration:index')

    if request.method == 'POST':
        form = LabelForm(request.POST, label_type=label_type)
        if form.is_valid():
            try:
                label = form.save(commit=False)
                label.type = label_type
                label.save()
                messages.success(request, f"Label '{label.name}' added successfully for {label_type}.")
                return redirect('configuration:manage_labels', label_type=label_type)
            except Exception as e:
                messages.error(request, f"Error adding label: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LabelForm(label_type=label_type) # Pass label_type for initial value in HiddenInput

    labels = Label.objects.filter(type=label_type).order_by('name')
    label_type_display = dict(LABEL_TYPES).get(label_type, label_type.capitalize())

    context = {
        'form': form,
        'labels': labels,
        'label_type': label_type,
        'label_type_display': label_type_display,
        'section_type': label_type
    }
    return render(request, 'configuration/manage_labels.html', context)

@staff_member_required
def edit_label(request, label_id):
    """
    Handles editing an existing label.
    """
    label = get_object_or_404(Label, pk=label_id)
    original_label_type = label.type # To redirect back to the correct section

    if request.method == 'POST':
        # Ensure type cannot be changed via this form if that's the design
        form = LabelForm(request.POST, instance=label, label_type=label.type) # Pass label_type to ensure 'type' field is handled correctly
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Label '{label.name}' updated successfully.")
                return redirect('configuration:manage_labels', label_type=original_label_type)
            except Exception as e:
                 messages.error(request, f"Error updating label: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LabelForm(instance=label, label_type=label.type)

    label_type_display = dict(LABEL_TYPES).get(label.type, label.type.capitalize())

    context = {
        'form': form,
        'label': label,
        'label_type': label.type,
        'label_type_display': label_type_display,
        'section_type': label.type # for manage_labels.html compatibility
    }
    # Reusing manage_labels.html for edit, it has logic for add/edit based on form.instance.pk
    return render(request, 'configuration/manage_labels.html', context)

@staff_member_required
def delete_label(request, label_id):
    """
    Handles deleting an existing label.
    """
    label = get_object_or_404(Label, pk=label_id)
    original_label_type = label.type # To redirect back to the correct section

    if request.method == 'POST':
        try:
            label_name = label.name
            label.delete()
            messages.success(request, f"Label '{label_name}' deleted successfully.")
            return redirect('configuration:manage_labels', label_type=original_label_type)
        except Exception as e:
            messages.error(request, f"Error deleting label: {e}")
            return redirect('configuration:manage_labels', label_type=original_label_type)
    else:
        # For GET, typically a confirmation page is shown.
        # For simplicity here, we'll just disallow GET for delete or redirect.
        # Or render a small confirmation form/message if manage_labels.html can be adapted.
        # For now, only POST is handled for deletion.
        # messages.info(request, "To delete a label, please use the delete button on the confirmation page (not yet implemented).")
        # return redirect('configuration:manage_labels', label_type=original_label_type)
        # Or, render a confirmation snippet within manage_labels perhaps, or a dedicated delete confirmation template.
        # For this subtask, we will assume POST only for delete.
        return HttpResponseNotAllowed(['POST'])
