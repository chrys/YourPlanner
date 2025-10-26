from django import forms
from django.forms.models import inlineformset_factory
from .models import Template, TemplateImage, TemplateItemGroup, TemplateItemGroupItem  # Added new models
from services.models import Service, Item  # Added Item import
from django.utils.translation import gettext_lazy as _

class TemplateForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
        help_text=_("Hold down 'Ctrl' (or 'Cmd' on Mac) to select more than one.")
    )
    
    number_of_groups = forms.IntegerField(  # New field for number of groups
        min_value=0,
        max_value=20,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_number_of_groups'
        }),
        help_text=_("Number of item groups for this template")
    )

    class Meta:
        model = Template
        fields = [
            'title', 'description', 'services',
            'base_price', 'currency', 'default_guests', 'price_per_additional_guest',
            'number_of_groups'  # Added to fields
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'services': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'default_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price_per_additional_guest': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'services': _("Hold down 'Ctrl' (or 'Cmd' on Mac) to select more than one."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for number_of_groups if editing existing template
        if self.instance and self.instance.pk:
            self.fields['number_of_groups'].initial = self.instance.item_groups.count()


class TemplateItemGroupForm(forms.ModelForm):  # New form for item groups
    """Form for creating/editing a template item group."""
    items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select items for this group")
    )

    class Meta:
        model = TemplateItemGroup
        fields = ['name', 'mandatory_count', 'items']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Main Course')}),
            'mandatory_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        professional = kwargs.pop('professional', None)
        super().__init__(*args, **kwargs)
        if professional:
            self.fields['items'].queryset = Item.objects.filter(
                service__professional=professional,
                is_active=True
            ).select_related('service').order_by('service__title', 'title')
        # Only set initial if instance exists and has a pk
        if self.instance and self.instance.pk:  # Only access items if pk exists
            self.fields['items'].initial = self.instance.items.values_list('item_id', flat=True)

    def clean(self):
        cleaned_data = super().clean()
        mandatory_count = cleaned_data.get('mandatory_count', 0)
        items = cleaned_data.get('items', [])
        # Only validate if items is a list (form is bound)
        if items and mandatory_count > len(items):
            raise forms.ValidationError(
                _("Mandatory count (%(count)d) cannot exceed the number of selected items (%(total)d).") 
                % {'count': mandatory_count, 'total': len(items)}
            )
        return cleaned_data


# Formset for handling multiple item groups
TemplateItemGroupFormSet = inlineformset_factory(
    Template,
    TemplateItemGroup,
    form=TemplateItemGroupForm,
    extra=0,  # No extra forms by default
    can_delete=True,
    min_num=0,
    validate_min=True,
)

# Formset for handling multiple images
TemplateImageFormSet = inlineformset_factory(
    Template,
    TemplateImage,
    fields=('image', 'is_default'),
    extra=1,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)