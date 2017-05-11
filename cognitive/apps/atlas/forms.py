from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Reset, Submit

class ImplementationForm(forms.Form):
    uri = forms.URLField(required=True)
    name = forms.CharField(required=True)
    description = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ImplementationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-implementationform'
        self.helper.form_method = 'post'
        self.helper.form_class = 'hidden'
        self.helper.form_action = 'add_task_implementation'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('implementation-cancel', 'Cancel'))
