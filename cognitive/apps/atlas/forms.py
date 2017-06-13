from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Reset, Submit

from cognitive.apps.atlas.query import Assertion, Disorder, Task

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

class CitationForm(forms.Form):
    citation_url = forms.URLField(required=True)
    citation_comment = forms.CharField(required=False)
    citation_desc = forms.CharField(required=True)
    citation_authors = forms.CharField(required=False)
    citation_type = forms.CharField(required=False)
    citation_pubname = forms.CharField(required=False)
    citation_pubdate = forms.CharField(required=False)
    citation_pmid = forms.CharField(required=False)
    citation_source = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(CitationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('citation-cancel', 'Cancel'))

class DisorderForm(forms.Form):
    name = forms.CharField(required=True)
    definition = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(DisorderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('disorder-cancel', 'Cancel'))

class TheoryAssertionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TheoryAssertionForm, self).__init__(*args, **kwargs)
        assertions = Assertion()
        choices = [(x['id'], x['name']) for x in assertions.all()]
        self.fields['assertions'] = forms.ChoiceField(choices=choices)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('theory-assertion-cancel', 'Cancel'))

class TaskDisorderForm(forms.Form):
    def __init__(self, task_id, *args, **kwargs):
        super(TaskDisorderForm, self).__init__(*args, **kwargs)
        disorders = Disorder()
        tasks = Task()
        contrasts = tasks.get_relation(task_id, "HASCONTRAST")

        cont_choices = [(x['id'], x['name']) for x in contrasts]
        self.fields['contrasts'] = forms.ChoiceField(choices=cont_choices)

        dis_choices = [(x['id'], x['name']) for x in disorders.all()]
        self.fields['disorders'] = forms.ChoiceField(choices=dis_choices)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('task-disorder-cancel', 'Cancel'))

class TheoryForm(forms.Form):
    label = "Enter the name of the theory collection you wish to add: "
    name = forms.CharField(required=True, label=label)

    def __init__(self, *args, **kwargs):
        super(TheoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'id': 'theory-form'}
        self.helper.form_class = "hidden"
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('theory-cancel', 'Cancel'))

class BatteryForm(forms.Form):
    label = "Enter the name of the task collection you wish to add: "
    name = forms.CharField(required=True, label=label)

    def __init__(self, *args, **kwargs):
        super(BatteryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'id': 'battery-form'}
        self.helper.form_class = "hidden"
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-cancel', 'Cancel', type="button"))
