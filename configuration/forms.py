from django import forms
from .models import ConfigurationCategory, ConfigurationLabel
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field


class ConfigurationLabelForm(forms.ModelForm):
    """
    Form for creating and editing configuration labels.
    """
    class Meta:
        model = ConfigurationLabel
        fields = ['category', 'name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))
        self.helper.layout = Layout(
            Field('category'),
            Field('name'),
            Field('description'),
            Field('is_active'),
        )

