from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Reset, Submit

class ImplementationForm(forms.Form):
    uri = forms.URLField(required=True)
    name = forms.CharField(required=True)
    description = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ImplementationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('implementation-cancel', 'Cancel'))

class ExternalDatasetForm(forms.Form):
    name = forms.CharField(required=True)
    uri = forms.URLField(required=True)

    def __init__(self, *args, **kwargs):
        super(ExternalDatasetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('dataset-cancel', 'Cancel'))

class IndicatorForm(forms.Form):
    type = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(IndicatorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('indicator-cancel', 'Cancel'))


