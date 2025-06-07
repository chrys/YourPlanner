from django import forms
from django.forms import inlineformset_factory
from .models import Template, TemplateImage, TemplateService
from services.models import Service


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.professional = kwargs.pop('professional', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        template = super().save(commit=False)
        if self.professional:
            template.professional = self.professional
        if commit:
            template.save()
        return template


class TemplateImageForm(forms.ModelForm):
    class Meta:
        model = TemplateImage
        fields = ['image', 'is_default', 'alt_text', 'position']
        widgets = {
            'position': forms.NumberInput(attrs={'min': 0}),
        }


class TemplateServiceForm(forms.ModelForm):
    class Meta:
        model = TemplateService
        fields = ['service', 'position']
        widgets = {
            'position': forms.NumberInput(attrs={'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        self.professional = kwargs.pop('professional', None)
        super().__init__(*args, **kwargs)
        
        # Filter services to only show those belonging to the professional
        if self.professional:
            self.fields['service'].queryset = Service.objects.filter(
                professional=self.professional,
                is_active=True
            )


# Create formsets for inline forms
TemplateImageFormSet = inlineformset_factory(
    Template, 
    TemplateImage,
    form=TemplateImageForm,
    extra=1,
    can_delete=True
)

TemplateServiceFormSet = inlineformset_factory(
    Template, 
    TemplateService,
    form=TemplateServiceForm,
    extra=1,
    can_delete=True
)

