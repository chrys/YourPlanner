from django import forms
from labels.models import Label

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'description', 'color', 'label_type']
        widgets = {
            'label_type': forms.HiddenInput(), # Type will be set by the view based on URL
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        label_type = kwargs.pop('label_type', None)
        super().__init__(*args, **kwargs)
        if label_type:
            self.fields['label_type'].initial = label_type_arg

        # Ensure 'label_type' is not required by the form itself if initial is set,
        # as it's handled by the view. But it is required by the model.
        # The HiddenInput widget means the user won't see it,
        # and initial value will be submitted.
        # However, if we are editing an existing instance, 'label_type' will be populated.
        if self.instance and self.instance.pk:
             self.fields['label_type'].disabled = True # Cannot change type of existing label via this form

        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['color'].widget.attrs.update({'class': 'form-control form-control-color'})
