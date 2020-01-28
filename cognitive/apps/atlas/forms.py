from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, HTML, Layout, Field, Reset, Submit, Button

from cognitive.apps.atlas.query import Assertion, Disorder, Task, Battery, ConceptClass, Concept
import cognitive.apps.atlas.query as query


def set_field_html_name(cls, new_name):
    """
    This creates wrapper around the normal widget rendering,
    allowing for a custom field name (new_name).
    """
    old_render = cls.widget.render

    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    cls.widget.render = _widget_render_wrapper


class TaskForm(forms.Form):
    term_name = forms.CharField(required=True)
    definition_text = forms.CharField(required=True)


class ConceptForm(forms.Form):
    name = forms.CharField(required=True, label="Term:")
    definition_text = forms.CharField(required=True, widget=forms.Textarea(),
                                      label="Your Definition:")
    concept_class = ConceptClass()
    choices = [(x['id'], "-yes- " + str(x['name']))
               for x in concept_class.all()]
    choices.insert(0, (None, "-no-"))
    cc_label = "In your opinion, does this concept belong to a larger class of concepts?"
    concept_class = forms.ChoiceField(
        choices=choices, label=cc_label, required=False)

    def __init__(self, concept_id, *args, **kwargs):
        if not args[0].get('submit'):
            concept = Concept()
            con_class = concept.get_relation(concept_id, "CLASSIFIEDUNDER",
                                             label="concept_class")
            if con_class:
                args[0]['concept_class'] = con_class[0]['id']
        super(ConceptForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse(
            'update_concept', kwargs={'uid': concept_id, })
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('definition_text'),
                Field('concept_class'),
                Submit('submit', 'Submit'),
                Reset('concept-cancel', 'Cancel', type="reset"),
                css_class="formline",
            )
        )


class ContrastForm(forms.Form):
    name = forms.CharField(required=True)
    description = forms.CharField(required=True)


class ConditionForm(forms.Form):
    condition_text = forms.CharField(required=True)
    condition_description = forms.CharField(required=True)


class WeightForm(forms.Form):
    weight = forms.FloatField()

    def __init__(self, cond_id, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.weight_name = cond_id
        self.fields['weight'].label = label
        set_field_html_name(self.fields['weight'], self.weight_name)

    def clean_weight(self):
        data = self.data['weight']
        if not data:
            raise ValidationError('Missing input')
        return data


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
    doi = forms.CharField(required=False)

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
        behaviors = query.Behavior()
        traits = query.Trait()
        tasks = Task()
        contrasts = tasks.get_relation(task_id, "HASCONTRAST")

        cont_choices = [(x['id'], x['name']) for x in contrasts]
        self.fields['contrasts'] = forms.ChoiceField(choices=cont_choices)

        pheno_choices = []
        pheno_choices.extend(
            [(x['id'], ''.join([x['name'], " (Disorder)"])) for x in disorders.all()])
        pheno_choices.extend(
            [(x['id'], ''.join([x['name'], " (Behavior)"])) for x in behaviors.all()])
        pheno_choices.extend(
            [(x['id'], ''.join([x['name'], " (Trait)"])) for x in traits.all()])
        self.fields['disorders'] = forms.ChoiceField(choices=pheno_choices)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('task-disorder-cancel', 'Cancel'))


class TaskConceptForm(forms.Form):
    def __init__(self, task_id, *args, **kwargs):
        super(TaskConceptForm, self).__init__(*args, **kwargs)
        concept = Concept()
        tasks = Task()
        contrasts = tasks.get_relation(task_id, "HASCONTRAST")

        cont_choices = [(x['id'], x['name']) for x in contrasts]
        self.fields['concept-contrasts'] = forms.ChoiceField(
            choices=cont_choices)

        concept_choices = [(x['id'], x['name']) for x in concept.all()]
        self.fields['concept'] = forms.ChoiceField(choices=concept_choices)

        self.helper = FormHelper()
        self.helper.attrs = {'id': 'concept-form'}
        self.helper.form_class = "hidden"
        self.helper.form_action = reverse('add_task_concept',
                                          kwargs={'uid': task_id})
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('task-concept-cancel', 'Cancel'))


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
    type = forms.ChoiceField(
        choices=[('parent', 'Parent'), ('child', 'Child')])

    def __init__(self, name=None, *args, **kwargs):
        super(DisorderDisorderForm, self).__init__(*args, **kwargs)
        name = (name if name is not None else '')
        disorders = Disorder()
        type_choices = [
            ('parent', '{} is a kind of <selected disorder>'.format(name)),
            ('child', '<selected disorder> is a kind of {}'.format(name))
        ]
        dis_choices = [(x['id'], x['name']) for x in disorders.all()]
        self.fields['type'] = forms.ChoiceField(choices=type_choices)
        self.fields['disorders'] = forms.ChoiceField(choices=dis_choices)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('disorder-disorder-cancel', 'Cancel'))


class ExternalLinkForm(forms.Form):
    ''' an external link for a node. For disorders this link may describe the
        disorder in more detail'''
    uri = forms.URLField(
        required=True, label="Enter the full URL for the link")

    def __init__(self, *args, **kwargs):
        super(ExternalLinkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('link-cancel', 'Cancel'))


class ConceptClassForm(forms.Form):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ConceptClassForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('concept-class-cancel', 'Cancel'))
        self.helper.form_action = reverse('add_concept_class')


class DisambiguationForm(forms.Form):
    term1_name = forms.CharField(label="")
    term1_name_ext = forms.CharField(label="")
    term1_definition = forms.CharField(required=True, widget=forms.Textarea(),
                                       label="Original Term Description")
    term2_name = forms.CharField(label="")
    term2_name_ext = forms.CharField(label="")
    term2_definition = forms.CharField(required=True, widget=forms.Textarea(),
                                       label="New Term Description")

    def __init__(self, label, uid, term=None, *args, **kwargs):
        super(DisambiguationForm, self).__init__(*args, **kwargs)
        if term is not None:
            self.initial = {
                'term1_name': term['name'],
                'term2_name': term['name'],
                'term1_definition': term['definition_text']
            }
        self.helper = FormHelper()
        self.helper.add_input(Reset('disambiguate_cancel_button', 'Cancel'))
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_action = reverse('add_disambiguation',
                                          kwargs={'label': label, 'uid': uid})
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('term1_name', css_class='disam-name'),
                    HTML('('),
                    Field('term1_name_ext', css_class='disam-name-ext'),
                    HTML(')'),
                    css_class='name-ext-inputs'
                ),
                Field('term1_definition', css_class='disam-def'),
                Div(
                    Field('term2_name', css_class='disam-name'),
                    HTML('('),
                    Field('term2_name_ext', css_class='disam-name-ext'),
                    HTML(')'),
                    css_class='name-ext-inputs'
                ),
                Field('term2_definition', css_class='disam-def'),
                css_class='popstar',
            )
        )


class PhenotypeForm(forms.Form):

    name = forms.CharField(required=True, label="Phenotype Name:")
    definition = forms.CharField(required=True, widget=forms.Textarea(),
                                 label="Description:")
    choices = (("disorder", "Disorder"),
               ("trait", "Trait"), ("behavior", "Behavior"))
    type = forms.ChoiceField(
        choices=choices, label="Phenotype classification", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('phenotype-cancel-button', 'Cancel'))
        self.helper.form_action = reverse('add_phenotype')


class TraitForm(forms.Form):
    name = forms.CharField(required=True, label="Phenotype Name:")
    definition = forms.CharField(required=True, widget=forms.Textarea(),
                                 label="Description:")

    def __init__(self, uid, trait=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if trait is not None:
            self.initial = {
                'name': trait['name'],
                'definition': trait['definition']
            }
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('trait_cancel_button', 'Cancel'))
        self.helper.form_action = reverse('update_trait', kwargs={'uid': uid})


class BehaviorForm(forms.Form):
    name = forms.CharField(required=True, label="Phenotype Name:")
    definition = forms.CharField(required=True, widget=forms.Textarea(),
                                 label="Description:")

    def __init__(self, uid, behavior=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if behavior is not None:
            self.initial = {
                'name': behavior['name'],
                'definition': behavior['definition']
            }
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('behavior_cancel_button', 'Cancel'))
        self.helper.form_action = reverse(
            'update_behavior', kwargs={'uid': uid})


class DoiForm(forms.Form):
    doi = forms.CharField(required=True, label="DOI:")

    def __init__(self, uid, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('doi-cancel-button', 'Cancel'))
        self.helper.form_action = reverse('add_citation_doi',
                                          kwargs={'label': label, 'uid': uid})
