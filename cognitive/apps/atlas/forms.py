from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Reset, Submit

from cognitive.apps.atlas.query import Assertion, Disorder, Task, Battery

class TaskForm(forms.Form):
    term_name = forms.CharField(required=True)
    definition_text = forms.CharField(required=True)

class ConceptForm(TaskForm):
    pass

class ContrastForm(forms.Form):
    name = forms.CharField(required=True)

class ConditionForm(forms.Form):
    condition_text = forms.CharField(required=True)
    condition_description = forms.CharField(required=True)

class ImplementationForm(forms.Form):
    implementation_uri = forms.URLField(required=True)
    implementation_name = forms.CharField(required=True)
    implementation_description = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ImplementationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('implementation-cancel', 'Cancel'))

class ExternalDatasetForm(forms.Form):
    dataset_name = forms.CharField(required=True)
    dataset_uri = forms.URLField(required=True)

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
    definition = forms.CharField(required=True, widget=forms.Textarea())

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
        self.helper.form_action = reverse('add_theory')
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
        self.helper.form_action = reverse('add_battery')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-cancel', 'Cancel', type="button"))

class ConceptTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ConceptTaskForm, self).__init__(*args, **kwargs)

        tasks = Task()
        choices = [(x['id'], x['name']) for x in tasks.all()]
        self.fields['tasks'] = forms.ChoiceField(choices=choices)

        self.helper = FormHelper()
        self.helper.form_class = "hidden"
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-cancel', 'Cancel', type="button"))

class BatteryBatteryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BatteryBatteryForm, self).__init__(*args, **kwargs)

        batteries = Battery()
        choices = [(x['id'], x['name']) for x in batteries.all()]
        self.fields['batteries'] = forms.ChoiceField(choices=choices)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-cancel', 'Cancel', type="button"))

class BatteryTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BatteryTaskForm, self).__init__(*args, **kwargs)

        tasks = Task()
        choices = [(x['id'], x['name']) for x in tasks.all()]
        self.fields['tasks'] = forms.ChoiceField(choices=choices)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-task-cancel', 'Cancel',
                                    type="button"))


class ConceptContrastForm(forms.Form):
    def __init__(self, task_id, concept_id, *args, **kwargs):
        super(ConceptContrastForm, self).__init__(*args, **kwargs)
        tasks = Task()
        contrasts = tasks.get_relation(task_id, "HASCONTRAST")
        choices = [(x['id'], x['name']) for x in contrasts]
        self.fields['contrasts'] = forms.ChoiceField(choices=choices)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('battery-cancel', 'Cancel', type="button"))
        self.helper.form_action = reverse('add_concept_contrast',
                                          kwargs={'uid': concept_id, 'tid': task_id})

class DisorderDisorderForm(forms.Form):
    ''' form for relating disorders to themselves '''
    type = forms.ChoiceField(choices=[('parent', 'Parent'), ('child', 'Child')])
    def __init__(self, *args, **kwargs):
        super(DisorderDisorderForm, self).__init__(*args, **kwargs)
        disorders = Disorder()
        choices = [(x['id'], x['name']) for x in disorders.all()]
        self.fields['disorders'] = forms.ChoiceField(choices=choices)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('disorder-disorder-cancel', 'Cancel'))

class ExternalLinkForm(forms.Form):
    ''' an external link for a node. For disorders this link may describe the
        disorder in more detail'''
    uri = forms.URLField(required=True, label="Enter the full URL for the link")

    def __init__(self, *args, **kwargs):
        super(ExternalLinkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('link-cancel', 'Cancel'))
