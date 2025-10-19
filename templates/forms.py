from django import forms
from django.forms.models import inlineformset_factory
from .models import Template, TemplateImage
from services.models import Service  # Adjusted based on prior knowledge
from django.utils.translation import gettext_lazy as _

class TemplateForm(forms.ModelForm):
    # CHANGED: Define services field explicitly as ModelMultipleChoiceField to support queryset assignment
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
        help_text=_("Hold down 'Ctrl' (or 'Cmd' on Mac) to select more than one.")
    )

    class Meta:
        model = Template
        fields = [
            'title', 'description', 'services',
            'base_price', 'currency', 'default_guests', 'price_per_additional_guest'  # <-- Added fields
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'services': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),  # <-- Added widget
            'currency': forms.Select(attrs={'class': 'form-select'}),  # <-- Added widget
            'default_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),  # <-- Added widget
            'price_per_additional_guest': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),  # <-- Added widget
        }
        help_texts = {
            'services': _("Hold down 'Ctrl' (or 'Cmd' on Mac) to select more than one."),
        }

    def __init__(self, *args, **kwargs):
        # Assuming 'professional' is passed to the form or set on the instance before save
        # If the professional has a limited set of services they can offer, filter here.
        # For now, showing all services.
        super().__init__(*args, **kwargs)


# Formset for handling multiple images
# We will handle the 'is_default' logic in the view or by custom validation on the formset
TemplateImageFormSet = inlineformset_factory(
    Template,
    TemplateImage,
    fields=('image', 'is_default'),
    extra=1, # Number of empty forms to display
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)
