''' Functional views to create, update, and view the various types of terms
    and their relationships in cognitive atlas. '''
from collections import OrderedDict
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponse, HttpResponseNotFound,
                         HttpResponseNotAllowed, HttpResponseRedirect)
from django.shortcuts import redirect, render

from cognitive.apps.atlas.forms import (CitationForm, DisorderForm,
                                        ExternalDatasetForm,
                                        ImplementationForm, IndicatorForm,
                                        TaskDisorderForm, TheoryAssertionForm,
                                        TheoryForm, BatteryForm,
                                        ConceptTaskForm, ConceptContrastForm,
                                        DisorderDisorderForm, ExternalLinkForm,
                                        BatteryBatteryForm, BatteryTaskForm,
                                        ConceptForm)
import cognitive.apps.atlas.forms as forms
import cognitive.apps.atlas.query as query
from cognitive.apps.atlas.utils import (clean_html, add_update,
                                         get_paper_properties, InvalidDoiException)
from cognitive.apps.users.models import User
from cognitive.settings import DOMAIN, graph

Assertion = query.Assertion()
Battery = query.Battery()
Behavior = query.Behavior()
Citation = query.Citation()
Concept = query.Concept()
ConceptClass = query.ConceptClass()
Condition = query.Condition()
Contrast = query.Contrast()
Disorder = query.Disorder()
Disambiguation = query.Disambiguation()
ExternalDataset = query.ExternalDataset()
ExternalLink = query.ExternalLink()
Implementation = query.Implementation()
Indicator = query.Indicator()
Node = query.Node()
Task = query.Task()
Theory = query.Theory()
Trait = query.Trait()

def rank_check(user):
    ''' function called by function decorators to see if the user has
        permissions to make changes. '''
    try:
        return int(user.rank) > 2
    except ValueError:
        return False

def get_display_name(uid):
    user = User.objects.values_list('first_name', 'last_name', 'obfuscate').get(id=uid)
    if not user[2]:
        return "Anonymous"
    return "{}{}".format(user[0][0], user[1])

def get_creator(uid, label):
    node_class = node_class_lookup(label)
    try:
        creator_node = node_class.get_reverse_relation(uid, "CREATED", label="user")[0]
        creator = get_display_name(creator_node["id"])
    except IndexError:
        creator = None
    return creator



# VIEWS FOR ALL NODES #########################################################

def all_nodes(request, nodes, node_type, node_type_plural):
    '''all_nodes returns view with all nodes for node_type'''


    context = {
        'term_type': node_type,
        'term_type_plural': node_type_plural,
        'nodes': nodes,
    }

    return render(request, "atlas/all_terms.html", context)

def all_concepts(request):
    '''all_concepts returns page with list of all concepts'''

    concepts = Concept.all(order_by="name")
    return all_nodes(request, concepts, "concept", "concepts")

def all_tasks(request):
    '''all_tasks returns page with list of all tasks'''

    tasks = Task.all(order_by="name")
    return all_nodes(request, tasks, "task", "tasks")

def all_batteries(request):
    '''all_batteries returns page with list of all batteries'''

    batteries = Battery.all(order_by="name")
    return all_nodes(request, batteries, "battery", "batteries")


def all_theories(request):
    '''all_theories returns page with list of all theories'''

    theories = Theory.all(order_by="name")
    return all_nodes(request, theories, "theory", "theories")

def all_collections(request, return_context=False):
    '''all_collections returns page with list of all collections'''
    theories = Theory.all(order_by="name")
    batteries = Battery.all(order_by="name")

    context = {
        'theories': theories,
        'batteries': batteries,
        'theory_form': TheoryForm(),
        'battery_form': BatteryForm()
    }
    if return_context:
        return context

    return render(request, "atlas/all_collections.html", context)

def all_concept_classes(request, return_context=False):
    concept_classes = ConceptClass.all(order_by="name")
    for cc in concept_classes:
        concepts = ConceptClass.get_reverse_relation(cc['id'], 'CLASSIFIEDUNDER',
                                                     'concept')
        cc['concepts'] = concepts
    context = {
        'concept_classes': concept_classes,
        'concept_class_form': forms.ConceptClassForm
    }
    return render(request, "atlas/all_concept_classes.html", context)

def disorder_populate(disorders):
    ''' recursive function that fills a dictionary with all disorders and their
        children disorders'''
    if bool(disorders) is False:
        return None
    ret = OrderedDict()
    for dis in disorders:
        key = (str(dis.properties['id']), str(dis.properties['name']))
        children = [x.start_node for x in dis.match_incoming(rel_type="ISA")]
        if children:
            children.sort(key=lambda x: str.lower(x.properties['name']))
        ret[key] = disorder_populate(children)
    return ret

def all_disorders(request, return_context=False):
    '''all_disorders returns page with list of all disorders'''
    disorder_form = DisorderForm

    '''
    dis_records = graph.cypher.execute(
        "match (dis:disorder) where not (dis:disorder)-[:ISA]->() return dis order by dis.name"
    )
    top_level_disorders = [x['dis'] for x in dis_records]
    top_level_disorders.sort(key=lambda x: str.lower(x.properties['name']))
    disorders = disorder_populate(top_level_disorders)
    '''
    disorders = Disorder.all(order_by="name")
    traits = Trait.all(order_by="name")
    behaviors = Behavior.all(order_by="name")

    context = {
        'appname': "The Cognitive Atlas",
        'active': "disorders",
        'disorder_form': disorder_form,
        'disorders': disorders,
        'phenotype_form': forms.PhenotypeForm(),
        'traits': traits,
        'behaviors': behaviors
    }

    if return_context:
        return context
    return render(request, "atlas/all_disorders.html", context)

def all_contrasts(request):
    '''all_contrasts returns page with list of all contrasts'''
    fields = ""
    contrasts = Contrast.all(order_by="name", fields=fields)
    return all_nodes(request, contrasts, "contast", "contrasts")


# VIEWS BY LETTER #############################################################

def nodes_by_letter(request, letter, nodes, nodes_count, node_type):
    '''nodes_by_letter returns node view for a certain letter'''

    appname = "The Cognitive Atlas"
    context = {
        'appname': appname,
        'nodes': nodes,
        'letter': letter,
        'term_type': node_type[:-1],
        'filtered_nodes_count': nodes_count,
    }

    return render(request, "atlas/terms_by_letter.html", context)

def concepts_by_letter(request, letter):
    '''concepts_by_letter returns concept view for a certain letter'''
    concepts = Concept.filter(filters=[("name", "starts_with", letter)], order_by="name")
    concepts_count = len(concepts)
    return nodes_by_letter(request, letter, concepts, concepts_count, "concepts")

def tasks_by_letter(request, letter):
    '''tasks_by_letter returns task view for a certain letter'''
    tasks = Task.filter(filters=[("name", "starts_with", letter)], order_by="name")
    tasks_count = len(tasks)
    return nodes_by_letter(request, letter, tasks, tasks_count, "tasks")


# VIEWS FOR SINGLE NODES ##########################################################

def view_concept(request, uid, return_context=False):
    ''' detail view for a give concept '''
    try:
        concept = Concept.get(uid)[0]
    except IndexError:
        raise Http404("Concept does not exist")

    # For each measured by (contrast), get the task
    if "MEASUREDBY" in concept["relations"]:
        for c in range(len(concept["relations"]["MEASUREDBY"])):
            contrast = concept["relations"]["MEASUREDBY"][c]
            tasks = Contrast.get_tasks(contrast["id"])
            concept["relations"]["MEASUREDBY"][c]["tasks"] = tasks

    citations = Concept.get_relation(concept["id"], "HASCITATION")
    tasks = Concept.get_reverse_relation(concept["id"], "ASSERTS")
    contrasts = Concept.get_relation(concept["id"], "MEASUREDBY")

    assertions_no_cont = []
    are_kinds_of = Concept.get_reverse_relation(concept["id"], "KINDOF")
    are_parts_of = Concept.get_reverse_relation(concept["id"], "PARTOF")

    tasks = {}
    for contrast in contrasts:
        contrast_task = Contrast.get_reverse_relation(contrast["id"], "HASCONTRAST", "task")
        try:
            tasks[contrast_task[0]]
        except KeyError:
            tasks[contrast_task[0]] = []
        except IndexError:
            continue
        tasks[contrast_task[0]].append(contrast)

    context = {
        "creator": get_creator(uid, "concept"),
        "are_kinds_of": are_kinds_of,
        "are_parts_of": are_parts_of,
        "concept": concept,
        "assertions": tasks,
        "assertions_no_cont": assertions_no_cont,
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'concept'),
        "concept_task_form": ConceptTaskForm(),
        "concept_form": ConceptForm(concept["id"], concept)
    }

    if return_context is True:
        return context

    return render(request, 'atlas/view_concept.html', context)

def get_measured_by(contrasts, label):
    ret = {}
    for contrast in contrasts:
        label_node = Contrast.get_reverse_relation(contrast["id"], "MEASUREDBY", label)
        try:
            ret[label_node[0]]
        except KeyError:
            ret[label_node[0]] = []
        except IndexError:
            continue
        ret[label_node[0]].append(contrast)
    return ret

def get_hasdifference(contrasts):
    ret = {}
    for contrast in contrasts:
        label_node = Contrast.get_relation(contrast["id"], "HASDIFFERENCE", "disorder")
        try:
            ret[label_node[0]]
        except KeyError:
            ret[label_node[0]] = []
        except IndexError:
            continue
        ret[label_node[0]].append(contrast)
    return ret

def view_task(request, uid, return_context=False):
    ''' Detail view for a given task '''
    try:
        task = Task.get(uid)[0]
    except IndexError:
        raise Http404("Task does not exist")

    # Replace newlines with <br>, etc.
    task["definition_text"] = clean_html(task.get("definition_text", "No definition provided"))
    contrasts = Task.api_get_contrasts(task["id"])

    conditions = Task.get_conditions(task["id"])

    implementations = Task.get_relation(task["id"], "HASIMPLEMENTATION")
    datasets = Task.get_relation(task["id"], "HASEXTERNALDATASET")
    indicators = Task.get_relation(task["id"], "HASINDICATOR")
    citations = Task.get_relation(task["id"], "HASCITATION")
    disorders = get_hasdifference(contrasts)

    concepts = get_measured_by(contrasts, "concept")
    behaviors = get_measured_by(contrasts, "behavior")
    traits = get_measured_by(contrasts, "trait")

    context = {
        "task": task,
        "creator": get_creator(uid, "task"),
        "concepts": concepts,
        "contrasts": contrasts,
        "conditions": conditions,
        "implementations": implementations,
        "datasets": datasets,
        "domain": DOMAIN,
        "implementation_form": ImplementationForm(),
        "dataset_form": ExternalDatasetForm(),
        "indicator_form": IndicatorForm(),
        "indicators": indicators,
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'task'),
        "disorders": disorders,
        "traits": traits,
        "behaviors": behaviors,
        "task_disorder_form": TaskDisorderForm(uid),
        "task_concept_form": forms.TaskConceptForm(uid),
        "disambiguation_form": forms.DisambiguationForm("task", uid, task),
    }

    if return_context is True:
        return context
    return render(request, 'atlas/view_task.html', context)

def view_battery(request, uid, return_context=False):
    ''' detail view for a battery. '''
    try:
        battery = Battery.get(uid)[0]
    except IndexError:
        raise Http404("Theory does not exist")
    progenitors = Battery.get_relation(uid, "PARTOF")
    descendants = Battery.get_reverse_relation(uid, "PARTOF")
    indicators = Battery.get_relation(uid, "HASINDICATOR")
    constituent_tasks = Battery.get_reverse_relation(uid, "INBATTERY",
                                                     label='task')
    constituent_batteries = Battery.get_reverse_relation(uid, "INBATTERY",
                                                         label='battery')
    citations = Battery.get_relation(uid, "HASCITATION")

    context = {
        "battery": battery,
        "creator": get_creator(uid, "battery"),
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'battery'),
        "indicators": indicators,
        "indicator_form": IndicatorForm(),
        "progenitors": progenitors,
        "descendants": descendants,
        "constituent_tasks": constituent_tasks,
        "constituent_batteries": constituent_batteries,
        "task_form": BatteryTaskForm(),
        "battery_form": BatteryBatteryForm()
    }
    if return_context:
        return context
    return render(request, 'atlas/view_battery.html', context)

def view_theory(request, uid, return_context=False):
    ''' detail view for a given assertion '''
    try:
        theory = Theory.get(uid)[0]
    except IndexError:
        raise Http404("Theory does not exist")
    assertions = Theory.get_reverse_relation(uid, "INTHEORY")
    # test if logged in, this might be an expensive operation since choices
    # field is populated on each instantiation
    theory_assertions_form = TheoryAssertionForm()
    citations = Theory.get_relation(uid, "HASCITATION")
    referenced_terms = {}
    for asrt in assertions:
        pred = Assertion.get_relation(asrt['id'], "PREDICATE")
        subj = Assertion.get_relation(asrt['id'], "SUBJECT")
        if not pred or not subj:
            continue
        pred = pred[0]
        subj = subj[0]
        for term in [pred, subj]:
            term_node = graph.cypher.execute(
                "match (t) where t.id = '{}' return t".format(term['id'])
            ).one
            # we only ever create nodes with one label:
            node_type = [x for x in term_node.labels][0]
            url = reverse(node_type, kwargs={'uid': term['id']})
            if term['name'] in  referenced_terms:
                referenced_terms[term['name']][0] += 1
            else:
                referenced_terms[term['name']] = [1, url]

    context = {
        "theory": theory,
        "creator": get_creator(uid, "theory"),
        "assertions": assertions,
        "theory_assertions_form": theory_assertions_form,
        "referenced_terms": referenced_terms,
        "doi_form": forms.DoiForm(uid, 'theory'),
        "citations": citations,
    }
    if return_context is True:
        return context
    return render(request, 'atlas/view_theory.html', context)

def view_disorder(request, uid, return_context=False):
    ''' detail view for a given disorder '''
    try:
        disorder = Disorder.get(uid)[0]
    except IndexError:
        raise Http404("Disorder does not exist")
    contrasts = Disorder.get_reverse_relation(uid, "HASDIFFERENCE")
    parent_disorders = Disorder.get_relation(uid, "ISA")
    child_disorders = Disorder.get_reverse_relation(uid, "ISA")
    external_links = Disorder.get_relation(uid, "HASLINK")

    tasks = {}
    for contrast in contrasts:
        contrast_task = Contrast.get_reverse_relation(contrast["id"], "HASCONTRAST", "task")
        try:
            tasks[contrast_task[0]]
        except KeyError:
            tasks[contrast_task[0]] = []
        tasks[contrast_task[0]].append(contrast)

    citations = Disorder.get_relation(disorder["id"], "HASCITATION")
    context = {
        "disorder":disorder,
        "creator": get_creator(uid, "disorder"),
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'disorder'),
        "assertions": tasks,
        "disorder_form": DisorderDisorderForm(name=disorder['name']),
        "parent_disorders": parent_disorders,
        "child_disorders": child_disorders,
        "external_links": external_links,
        "external_link_form": ExternalLinkForm(),
    }

    if return_context:
        return context
    return render(request, 'atlas/view_disorder.html', context)

def view_trait(request, uid, return_context=False):
    try:
        trait = Trait.get(uid)[0]
    except IndexError:
        raise Http404("Trait does not exist")
    contrasts = Trait.get_relation(uid, "MEASUREDBY")
    external_links = Trait.get_relation(uid, "HASLINK")
    citations = Trait.get_relation(uid, "HASCITATION")

    tasks = {}
    for contrast in contrasts:
        contrast_task = Contrast.get_reverse_relation(contrast["id"], "HASCONTRAST", "task")
        try:
            tasks[contrast_task[0]]
        except KeyError:
            tasks[contrast_task[0]] = []
        tasks[contrast_task[0]].append(contrast)

    context = {
        "trait": trait,
        "creator": get_creator(uid, "trait"),
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'trait'),
        "assertions": tasks,
        "trait_form": forms.TraitForm(trait['id'], trait=trait),
        "external_links": external_links,
        "external_link_form": ExternalLinkForm(),
    }

    if return_context:
        return context
    return render(request, 'atlas/view_trait.html', context)

def view_behavior(request, uid, return_context=False):
    try:
        behavior = Behavior.get(uid)[0]
    except IndexError:
        raise Http404("Behavior does not exist")
    contrasts = Behavior.get_relation(uid, "MEASUREDBY")
    external_links = Behavior.get_relation(uid, "HASLINK")
    citations = Behavior.get_relation(uid, "HASCITATION")

    tasks = {}
    for contrast in contrasts:
        contrast_task = Contrast.get_reverse_relation(contrast["id"], "HASCONTRAST", "task")
        try:
            tasks[contrast_task[0]]
        except KeyError:
            tasks[contrast_task[0]] = []
        tasks[contrast_task[0]].append(contrast)

    context = {
        "behavior": behavior,
        "creator": get_creator(uid, "behavior"),
        "citations": citations,
        "doi_form": forms.DoiForm(uid, 'behavior'),
        "assertions": tasks,
        "behavior_form": forms.BehaviorForm(behavior['id'], behavior=behavior),
        "external_links": external_links,
        "external_link_form": ExternalLinkForm(),
    }

    if return_context:
        return context
    return render(request, 'atlas/view_behavior.html', context)


# ADD NEW TERMS ###################################################################

@login_required
@user_passes_test(rank_check, login_url='/403')
def contribute_term(request):
    '''contribute_term will return the contribution detail page for a term that is
    posted, or visiting the page without a POST will return the original form
    '''

    context = {"message":"Please specify the term you want to contribute."}

    if request.method == "POST":
        term_name = request.POST.get('newterm', '')

        # Does the term exist in the atlas?
        results = query.search(term_name)
        matches = [x["name"] for x in results if x["name"] == term_name]
        message = "Please further define %s" %(term_name)

        if len(matches) > 0:
            message = "Term %s already exists in the Cognitive Atlas." %(term_name)
            context["already_exists"] = "anything"

        context["message"] = message
        context["term_name"] = term_name
        context["other_terms"] = results

    return render(request, 'atlas/contribute_term.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_phenotype(request):
    '''  '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = forms.PhenotypeForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        properties = {"definition": cleaned_data['definition']}
        label = cleaned_data['type']
        new_pheno = Node.create(cleaned_data["name"], properties,
                                request=request, label=label)
        if new_pheno is None:
            messages.error(request, "Was unable to create {}".format(cleaned_data['type']))
            return all_disorders(request)
        if label == 'disorder':
            return view_disorder(request, new_pheno.properties["id"])
        elif label == 'trait':
            return view_trait(request, new_pheno.properties["id"])
        elif label == 'behavior':
            return view_behavior(request, new_pheno.properties["id"])
    else:
        # if form is not valid, regenerate context and use validated form
        context = all_disorders(request, return_context=True)
        context['phenotype_form'] = form
        return render(request, "atlas/all_disorders.html", context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def contribute_disorder(request):
    ''' contribute_disorder will return the detail page for the new disorder '''
    if request.method == "POST":
        disorder_form = DisorderForm(request.POST)
        if disorder_form.is_valid():
            cleaned_data = disorder_form.cleaned_data
            properties = {"definition": cleaned_data['definition']}
            new_dis = Disorder.create(cleaned_data["name"], properties, request=request)
            if new_dis is None:
                messages.error(request, "Was unable to create disorder")
                return all_disorders(request)
        else:
            # if form is not valid, regenerate context and use validated form
            context = all_disorders(request, return_context=True)
            context['disorder_form'] = disorder_form
            return render(request, "atlas/all_disorders.html", context)
    # redirect back to task/id?
    return view_disorder(request, new_dis.properties["id"])

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_term(request):
    '''add_term will add a new term to the atlas
    '''

    if request.method == "POST":
        term_type = request.POST.get('term_type', '')
        term_name = request.POST.get('term_name', '')
        definition_text = request.POST.get('definition_text', '')

        properties = None
        if definition_text != '':
            properties = {"definition_text": definition_text}

        if term_type == "concept":
            node = Concept.create(name=term_name, properties=properties, request=request)
            return redirect('concept', node["id"])

        elif term_type == "task":
            node = Task.create(name=term_name, properties=properties, request=request)
            return redirect('task', node["id"])

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_condition(request, task_id):
    '''add_condition will associate a condition with the given task
    :param task_id: the uid of the task, to return to the correct page after creation
    '''
    if request.method == "POST":
        relation_type = "HASCONDITION" #task --HASCONDITION-> condition
        condition_name = request.POST.get('condition_name', '')

        if condition_name != "":
            condition = Condition.create(name=condition_name, request=request)
            Task.link(task_id, condition["id"], relation_type, endnode_type="condition")
    return view_task(request, task_id)


# UPDATE TERMS ####################################################################

@login_required
@user_passes_test(rank_check, login_url='/403')
def set_reviewed(request, uid, label):
    ''' Concepts and tasks can be marked as reviewed by users to show they have
        been vetted '''
    Node.update(uid, {'review_status': 'True'}, label=label)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@user_passes_test(rank_check, login_url='/403')
def set_unreviewed(request, uid, label):
    ''' revoke reviewed status of concept or task. '''
    Node.update(uid, {'review_status': 'False'}, label=label)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_concept(request, uid):
    ''' Take concept form, check for making new concept class relation, pass
        rest of form fields to query update function. '''
    if request.method != "POST":
        return redirect('concept', uid)

    concept_form = ConceptForm(uid, request.POST)

    if concept_form.is_valid():
        cleaned_data = concept_form.cleaned_data
        con_class_id = cleaned_data.pop('concept_class')
        for rel in Concept.get_relation(uid, "CLASSIFIEDUNDER", label="concept_class"):
            Concept.unlink(uid, rel['id'], "CLASSIFIEDUNDER", "concept_class")
        Concept.link(uid, con_class_id, "CLASSIFIEDUNDER", "concept_class")
        Concept.update(uid, cleaned_data)
        return redirect('concept', uid)
    else:
        context = view_concept(request, uid, return_context=True)
        context['concept_form'] = concept_form
        return render(request, 'atlas/view_concept.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_trait(request, uid):
    if request.method != "POST":
        return redirect('concept', uid)
    try:
        trait = Trait.get(uid)[0]
    except IndexError:
        raise Http404("Trait does not exist")
    form = forms.TraitForm(uid, data=request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        Trait.update(uid, updates={'name': cleaned_data['name'], 'definition': cleaned_data['definition']})
        return redirect('view_trait', uid=uid)
    else:
        return redirect('view_trait', uid=uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_behavior(request, uid):
    if request.method != "POST":
        return redirect('concept', uid)
    try:
        behavior = Behavior.get(uid)[0]
    except IndexError:
        raise Http404("Behavior does not exist")
    form = forms.BehaviorForm(uid, data=request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        Behavior.update(uid, updates={'name': cleaned_data['name'], 'definition': cleaned_data['definition']})
        return redirect('view_behavior', uid=uid)
    else:
        return redirect('view_behavior', uid=uid)



@login_required
@user_passes_test(rank_check, login_url='/403')
def update_task(request, uid):
    if request.method == "POST":
        definition = request.POST.get('definition_text', '')
        updates = add_update("definition_text", definition)
        Task.update(uid, updates=updates)
    return view_task(request, uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_theory(request, uid):
    if request.method == "POST":
        collection_description = request.POST.get('collection_description', '')
        name = request.POST.get('theory_name', '')
        updates = add_update("name", name)
        updates = add_update("collection_description", collection_description,
                             updates)
        Theory.update(uid, updates=updates)
    return view_theory(request, uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_battery(request, uid):
    if request.method == "POST":
        description = request.POST.get('description', '')
        updates = add_update("collection_description", description)
        Battery.update(uid, updates=updates)
    return view_battery(request, uid)


@login_required
@user_passes_test(rank_check, login_url='/403')
def update_disorder(request, uid):
    if request.method == "POST":
        definition = request.POST.get('disorder_definition', '')
        name = request.POST.get('disorder_name', '')
        updates = add_update("name", name)
        updates = add_update("definition", definition, updates)
        Disorder.update(uid, updates=updates)
    return view_disorder(request, uid)

# ADD RELATIONS ###################################################################

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_concept_relation(request, uid):
    '''add_concept_relation will add a relation from a concept to another concept (PARTOF or KINDOF)
    :param uid: the uid of the concept page, for returning to the page after creation
    '''
    if request.method == "POST":
        relation_type = request.POST.get('relation_type', '')
        concept_selection = request.POST.get('concept_selection', '')
        if relation_type.startswith("REV"):
            Concept.link(concept_selection, uid, relation_type[3:])
        else:
            Concept.link(uid, concept_selection, relation_type)
    return view_concept(request, uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_contrast(request, uid):
    ''' add_task_contrast will display the view to add a contrast to a
        task, meaning a set of conditions and an operator over the
        conditions. This view is a box over the faded out view_task page
    :param uid: the unique id of the task
    '''
    context = view_task(request, uid, return_context=True)
    context["conditions"] = Task.get_conditions(uid)
    return render(request, 'atlas/add_contrast.html', context)


@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_concept(request, uid):
    '''add_task_concept will add a cognitive concept to the list on a
       task page, making the assertion that the concept is associated
       with the task.
    :param uid: the unique id of the task, for returning to the task page when finished
    '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = forms.TaskConceptForm(uid, request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        concept_id = cleaned_data['concept']
        cont_id = cleaned_data['concept-contrasts']
        Concept.link(concept_id, cont_id, "MEASUREDBY", endnode_type="contrast")
        return redirect('view_task', uid=uid)
    else:
        context = view_task(request, uid, return_context=True)
        context['task_concept_form'] = form
        return render(request, 'atlas/view_task.html', context)



@login_required
@user_passes_test(rank_check, login_url='/403')
def add_concept_task(request, concept_id):
    '''add_concept_task will add a cognitive task to the list on a
       concept page, making the assertion that the task is associated
       with the concept.
    :param concept_id: the unique id of the task, for returning to the task page when finished
    '''
    if request.method == "POST":
        relation_type = "ASSERTS" #task --asserts-> concept
        task_selection = request.POST.get('task_selection', '')
        Task.link(task_selection, concept_id, relation_type, endnode_type="concept")
    return view_concept(request, concept_id)

@login_required
@user_passes_test(rank_check, login_url='/403')
def link_disam(request, label, uid):
    ''' link_disam_task will create a link between an existing disambiguation
        page and an existing task.
    :param uid: the unique id of the disambiguation
    '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "DISAMBIGUATES"
    selection = request.POST.get('selection', '')
    Disambiguation.link(uid, selection, relation_type, endnode_type=label)
    return redirect('view_disambiguation', uid=uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def unlink_disam(request, label, uid, tid):
    ''' link_disam_task will create a link between an existing disambiguation
        page and an existing task.
    :param uid: the unique id of the disambiguation
    '''
    relation_type = "DISAMBIGUATES"
    unlink_ret = Disambiguation.unlink(uid, tid, relation_type, endnode_type=label)
    if unlink_ret is not None:
        messages.error(request, "Was unable to unlink node, received error {}".format(unlink_ret))
    return redirect('view_disambiguation', uid=uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_disorder_task(request, disorder_id):
    '''add_disorder_task will add a cognitive task to the list on a
       disorder page, making the assertion that the task is associated
       with the disorder.
    :param disorder_id: the unique id of the task, for returning to the task page when finished
    '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "ASSERTS" #task --asserts-> disorder
    task_selection = request.POST.get('task_selection', '')
    Task.link(task_selection, disorder_id, relation_type, endnode_type="disorder")
    assertion = graph.cypher.execute(
        (
            "match (t:task)<-[:PREDICATE]-(a:assertion)-[:SUBJECT]->(d:disorder)"
            " where d.id = '{}' and t.id = '{}' return a "
        ).format(disorder_id, task_selection)
    )
    if assertion.records == []:
        asrt = Assertion.create("", request=request)
        Assertion.link(asrt.properties['id'], disorder_id, "SUBJECT", endnode_type='disorder')
        Assertion.link(asrt.properties['id'], task_selection, "PREDICATE", endnode_type='task')

    return redirect('disorder', disorder_id)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_disorder_disorder(request, disorder_id):
    ''' process form from disorder view that relates disorders to disorders '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = DisorderDisorderForm(data=request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        rel_dis_id = cleaned_data['disorders']
        rel_type = cleaned_data['type']
        if rel_type == 'parent':
            Disorder.link(disorder_id, rel_dis_id, "ISA", "disorder")
        else:
            Disorder.link(rel_dis_id, disorder_id, "ISA", "disorder")
        return view_disorder(request, disorder_id)
    else:
        context = view_disorder(request, disorder_id, return_context=True)
        context['disorder_form'] = form
        return render(request, 'atlas/view_disorder.html', context)


    return redirect('disorder', disorder_id)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_concept_contrast(request, uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "MEASUREDBY"
    contrast_selection = request.POST.get('contrast-selection', '')
    Concept.link(uid, contrast_selection, relation_type, endnode_type="contrast")
    return redirect('concept', uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_concept_contrast_task(request, uid):
    '''add_concept_contrast will add a contrast associated with conditions--> task via the task view
    :param uid: the uid of the task, to return to the correct page after creation
    '''
    if request.method == "POST":
        relation_type = "MEASUREDBY" #concept --MEASUREDBY-> contrast
        contrast_selection = request.POST.get('contrast_selection', '')
        concept_id = request.POST.get('concept_id', '')
        con_link = Concept.link(concept_id, contrast_selection, relation_type,
                                endnode_type="contrast")
        if con_link is not None:
            concept_task_contrast_assertion(request, concept_id, uid, contrast_selection)
    return view_task(request, uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def concept_task_contrast_assertion(request, concept_id, task_id, contrast_id):
    ''' function to generate assertion node along with all three relations
        assocaited with it. Link function will not create duplicate links if
        they already exist.'''
    asrt = Assertion.create("", request=request)
    Assertion.link(asrt.properties['id'], concept_id, "SUBJECT", endnode_type='concept')
    Assertion.link(asrt.properties['id'], task_id, "PREDICATE", endnode_type='task')
    Assertion.link(asrt.properties['id'], contrast_id, "PREDICATE_DEF", endnode_type='contrast')

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_contrast(request, task_id):
    '''add_contrast is the function called when the user submits a set
       of conditions and an operator to specify a new contrast.
    :param task_id: the id of the task, to return to the correct page after submission
    '''
    if request.method == "POST":
        relation_type = "HASCONTRAST" #condition --HASCONTRAST-> contrast

        #pickle.dump(post, open('result.pkl', 'wb'))
        contrast_name = request.POST.get('contrast_name', '')
        skip = ["contrast_name", "csrfmiddlewaretoken"]

        # Get dictionary with new conditions with nonzero weights
        conditions = dict()
        condition_ids = [x for x in request.POST.keys() if x not in skip]
        for condition_id in condition_ids:
            weight = float(request.POST.get(condition_id, 0))
            if weight != 0:
                conditions[condition_id] = weight

        if contrast_name != "" and len(conditions) > 0:
            node = Contrast.create(name=contrast_name, request=request)
            # Associate task and contrast so we can look it up for task view
            Task.link(task_id, node.properties["id"], relation_type, endnode_type="contrast")

            # Make a link between contrast and conditions, specify side as property of relation
            for condition_id, weight in conditions.items():
                properties = {"weight":weight}
                Condition.link(condition_id, node["id"], relation_type,
                               endnode_type="contrast", properties=properties)

    return view_task(request, task_id)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_disorder(request, task_id):
    ''' From the task we can create a link between the task we are viewing and
        a disorder.'''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    task_disorder_form = TaskDisorderForm(task_id, request.POST)
    if task_disorder_form.is_valid():
        cleaned_data = task_disorder_form.cleaned_data
        phenotype_id = cleaned_data['disorders']
        cont_id = cleaned_data['contrasts']
        if phenotype_id[:3] == 'dso':
            node_type = 'disorder'
        elif phenotype_id[:3] == 'bvr':
            node_type = 'behavior'
        elif phenotype_id[:3] == 'trt':
            node_type = 'trait'
        else:
            node_type = 'trait'

        if node_type == 'disorder':
            Contrast.link(cont_id, phenotype_id, "HASDIFFERENCE", endnode_type=node_type)
        else:
            node_class_lookup(node_type).link(phenotype_id, cont_id,
                                              "MEASUREDBY", endnode_type='contrast')
        return redirect(view_task, task_id)
    else:
        context = view_task(request, task_id, return_context=True)
        context['task_disorder_form'] = task_disorder_form
        return render(request, 'atlas/view_task.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_concept_class(request):
    ''' Concept classes from the old database have name and description fields
        they always match. We will continue to store the name as a description
        for the time being.
    '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = forms.ConceptClassForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        name = cleaned_data.pop('name')
        ConceptClass.create(name, properties={'description': name},
                            request=request)
        return redirect('all_concept_classes')
    else:
        context = all_concept_classes(request, return_context=True)
        context['concept_class_form'] = form
        return render(request, 'atlas/concept_class.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_disambiguation(request, label, uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    form = forms.DisambiguationForm(label, uid, data=request.POST, term=None)

    if not form.is_valid():
        if label == "task":
            context = view_task(request, uid, return_context=True)
            context['disambiguation_form'] = form
            return render(request, 'atlas/view_task.html', context)
        elif label == "concept":
            context = view_concept(request, uid, return_context=True)
            context['disambiguation_form'] = form
            return render(request, 'atlas/view_concept.html', context)
        else:
            return HttpResponseNotFound(content='label in request has no disambiguation response')

    cleaned_data = form.cleaned_data
    terms = Node.get(uid, label=label)
    if len(terms) < 1:
        raise Exception("to short")
        return HttpResponseNotFound('Uid {} with label {} not found'.format(uid, label))
    else:
        orig_node = terms[0]
        orig_id = orig_node['id']
    # copy orig term
    new_node_name = "{} ({})".format(
        cleaned_data['term2_name'],
        cleaned_data['term2_name_ext']
    )
    new_node = Node.create(new_node_name,
                           {"definition_text": cleaned_data['term2_definition']},
                           label=label, request=request)
    new_id = new_node.properties['id']

    # update orig term name
    new_node_name = "{} ({})".format(
        cleaned_data['term1_name'],
        cleaned_data['term1_name_ext']
    )

    Node.update(
        orig_node['id'],
        {"name": new_node_name, "definition_text": cleaned_data['term1_definition']},
        label=label
    )
    # new disambiguation node
    disam = Disambiguation.create(cleaned_data['term1_name'], request=request)
    disam_id = disam.properties['id']

    # link terms to disambig
    Disambiguation.link(disam_id, new_id, "DISAMBIGUATES", label)
    Disambiguation.link(disam_id, orig_id, "DISAMBIGUATES", label)
    return redirect("view_disambiguation", uid=disam_id)

def view_disambiguation(request, uid):
    try:
        disam = Disambiguation.get(uid)[0]
    except IndexError:
        raise Http404("Concept does not exist")

    context = {
        "disam": disam,
    }

    try:
        rel_id = disam['relations']['DISAMBIGUATES'][0]['id']
    except (KeyError, IndexError) as e:
        # disambiguation isn't disambiguating anything.
        pass

    rel_node = Task.get(rel_id)

    # now disambiguation only happens on tasks and concepts. If the id is found
    # to be a task we use the task version of the disam template, otherwise the
    # the concept version is used. Future might be best to have query node agnostic
    # search to derive the proper label.
    if len(rel_node) > 0:
        return render(request, 'atlas/view_task_disambiguation.html', context)
    else:
        return render(request, 'atlas/view_concept_disambiguation.html', context)


@login_required
@user_passes_test(rank_check, login_url='/403')
def make_link(request, src_id, src_label, dest_label, form_class, name_field,
              view, rel, reverse=False, create=True):
    ''' make link processes forms in a request and attempts to create links
        between nodes. If create is True, make link will crate a node based on
        the form. If create is false it will attempt to find an existing node
        using 'name_field' in the form as the id to lookup the node by.'''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = form_class(request.POST)
    if not form.is_valid():
        return view(request, src_id)
    clean_data = form.cleaned_data

    if create is True:
        dest_node = dest_label.create(clean_data[name_field],
                                      properties=clean_data, request=request)
    else:
        dest_node = graph.find_one(dest_label.name, "id", clean_data[name_field])

    if dest_node is None:
        messages.error(request, "Was unable to create {}".format(dest_label.name))
        return view(request, src_id)

    if reverse is False:
        link_made = src_label.link(src_id, dest_node.properties['id'],
                                   rel, endnode_type=dest_label.name)
    elif reverse is True:
        link_made = dest_label.link(dest_node.properties['id'], src_id,
                                    rel, endnode_type=src_label.name)

    if link_made is None:
        graph.delete(dest_node)
        error_msg = "Was unable to associate {} and {}".format(
            src_label.name, dest_label.name)
        messages.error(request, error_msg)
    return view(request, src_id)


@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_implementation(request, task_id):
    ''' From the task view we can create an implementation that is associated
        with a given task'''
    return make_link(request, task_id, Task, Implementation,
                     ImplementationForm, 'implementation_name', view_task,
                     "HASIMPLEMENTATION")

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_dataset(request, task_id):
    ''' From the task view we can create a link to dataset that is associated
        with a given task'''
    return make_link(request, task_id, Task, ExternalDataset,
                     ExternalDatasetForm, 'dataset_name', view_task,
                     "HASEXTERNALDATASET")

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_task_indicator(request, task_id):
    ''' From the task view we can create a link to indicator that is associated
        with a given task.'''
    return make_link(request, task_id, Task, Indicator, IndicatorForm,
                     'type', view_task, "HASINDICATOR")

# need to add ExternalLink to query and make form
@login_required
@user_passes_test(rank_check, login_url='/403')
def add_disorder_external_link(request, disorder_id):
    ''' From the task view we can create a link to citation that is associated
        with a given task.'''
    return make_link(request, disorder_id, Disorder, ExternalLink,
                     ExternalLinkForm, 'uri', view_disorder, "HASLINK")

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_battery_indicator(request, battery_id):
    return make_link(request, battery_id, Battery, Indicator, IndicatorForm,
                     'type', view_battery, "HASINDICATOR")

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_battery_battery(request, battery_id):
    return make_link(request, battery_id, Battery, Battery, BatteryBatteryForm,
                     'batteries', view_battery, "INBATTERY", reverse=True,
                     create=False)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_battery_task(request, battery_id):
    return make_link(request, battery_id, Battery, Task, BatteryTaskForm,
                     'tasks', view_battery, "INBATTERY", reverse=True,
                     create=False)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_trait_contrast(request, uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "MEASUREDBY"
    contrast_selection = request.POST.get('contrast-selection', '')
    Trait.link(uid, contrast_selection, relation_type, endnode_type="contrast")
    return redirect('view_trait', uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_behavior_contrast(request, uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "MEASUREDBY"
    contrast_selection = request.POST.get('contrast-selection', '')
    Behavior.link(uid, contrast_selection, relation_type, endnode_type="contrast")
    return redirect('view_behavior', uid)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_disorder_contrast(request, uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    relation_type = "HASDIFFERENCE"
    contrast_selection = request.POST.get('contrast-selection', '')
    Contrast.link(contrast_selection, uid, relation_type, endnode_type="disorder")
    return redirect('disorder', uid)


@login_required
@user_passes_test(rank_check, login_url='/403')
def add_theory_assertion(request, theory_id):
    ''' from theory detail view we can add assertions to the theory that we
        are looking at. '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    theory_assertion_form = TheoryAssertionForm(request.POST)
    if theory_assertion_form.is_valid():
        cleaned_data = theory_assertion_form.cleaned_data
        assertion_id = cleaned_data['assertions']
        Assertion.link(assertion_id, theory_id, "INTHEORY", endnode_type="theory")
        return view_theory(request, theory_id)
    else:
        context = view_theory(request, theory_id, return_context=True)
        context['theory_assertion_form'] = theory_assertion_form
        return render(request, 'atlas/view_theory.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_theory(request):
    ''' from all collections we can add new theories, this view handles that '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    theory_form = TheoryForm(request.POST)
    if theory_form.is_valid():
        cleaned_data = theory_form.cleaned_data
        name = cleaned_data['name']
        new_theory = Theory.create(name, request=request)
        return view_theory(request, new_theory.properties['id'])
    else:
        context = all_collections(request, return_context=True)
        context['theory_form'] = theory_form
        return render(request, 'atlas/all_collections.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_battery(request):
    ''' from all collections we can add new theories, this view handles that '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    battery_form = TheoryForm(request.POST)
    if battery_form.is_valid():
        cleaned_data = battery_form.cleaned_data
        name = cleaned_data['name']
        new_battery = Battery.create(name, request=request)
        return view_battery(request, new_battery.properties['id'])
    else:
        context = all_collections(request, return_context=True)
        context['battery_form'] = battery_form
        return render(request, 'atlas/all_collections.html', context)

@login_required
@user_passes_test(rank_check, login_url='/403')
def add_citation_doi(request, label, uid):
    view = "view_{}".format(label)

    form = forms.DoiForm(label, uid, request.POST)
    if form.is_valid() is False:
        messages.error(request, "The doi provided is invalid.")
        return redirect(view, uid)

    doi = form.cleaned_data['doi']

    properties = ()
    try:
        properties = get_paper_properties(doi)
    except InvalidDoiException:
        messages.error(request, "Unable to find DOI {}".format(doi))
        return redirect(view, uid)
    try:
        form_props = {
            'citation_desc': properties[0],
            'citation_authors': properties[1],
            'citation_url': properties[2],
            'citation_pubdate': properties[3],
            'citation_pubname': properties[4],
        }
    except IndexError:
        messages.error(request, "Unable to retrieve all necessary information from DOI {}".format(doi))
        return redirect(view, uid)

    post = request.POST.copy()
    post.update(form_props)
    request.POST = post
    node_class = node_class_lookup(label)
    if node_class is None:
        messages.error(
            request,
            "Operation could not be performed on node label {}".format(label)
        )
        return redirect(view, uid)
    view_func = node_view_lookup(label)
    if view_func is None:
        messages.error(request,
                       "Detail view for {} could not be found".format(label))
        return redirect(view, uid)
    return make_link(request, uid, node_class, Citation, CitationForm,
                     'citation_desc', view_func, "HASCITATION")


def view_contrast(request, uid):
    task = Contrast.get_tasks(uid)[0]
    if not task:
        raise Http404("Contrast has no parent task")
    return redirect(view_task, task['task_id'])

@login_required
@user_passes_test(rank_check, login_url='/403')
def update_contrast(request, uid):
    try:
        contrast = Contrast.get(uid)[0]
    except IndexError:
        raise Http404("Contrast does not exist")

    conditions = Contrast.get_conditions(uid)
    task = Contrast.get_tasks(uid)[0]
    if request.method == 'GET':
        condition_forms = []
        for condition in conditions:
            form = forms.WeightForm(
                condition['condition_id'],
                label=condition['condition_name'],
                data={'weight': condition['r_weight']}
            )
            condition_forms.append(form)
        context = {
            'condition_forms': condition_forms,
            'contrast': contrast,
            'task': task
        }
        return render(request, "atlas/update_contrast.html", context)
    elif request.method == "POST":
        for condition in conditions:
            cond_id = condition['condition_id']
            if request.POST.get(cond_id, None):
                weight = request.POST[cond_id]
                Condition.update_link_properties(cond_id, uid, "HASCONTRAST", "contrast",
                                                 {'weight': weight})
        return redirect(view_task, task['task_id'])
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

# SEARCH TERMS ################################################################

def search_all(request):
    ''' used by templates via ajax when searching for terms '''
    data = "no results"
    search_text = request.POST.get("searchterm", "")
    results = []
    if search_text != '':
        results = query.search(search_text)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def search_by_type(request, node_type):
    ''' Used by ajax in the templates when adding concepts to a task '''
    data = "no results"
    search_text = request.POST.get("relationterm", "")
    results = []
    if search_text != '':
        results = query.search(search_text, node_type=node_type)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def search_concept(request):
    ''' Used by ajax in the templates when adding concepts to a task '''
    return search_by_type(request, "concept")

def search_task(request):
    ''' Used by ajax in the templates when adding concepts to a task '''
    return search_by_type(request, "task")

def search_contrast(request):
    data = "no results"
    search_text = request.POST.get("relationterm", "")
    results = []
    if search_text != '':
        results = query.search_contrast(search_text)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def node_class_lookup(label):
    ''' Some functions have access to a string representation of a label, this
        function converts that string to a an instance of a Node class '''
    lookup_table = {
        'task': Task,
        'concept': Concept,
        'disorder': Disorder,
        'behavior': Behavior,
        'trait': Trait,
        'theory': Theory,
        'battery': Battery,
    }
    try:
        return lookup_table[label]
    except KeyError:
        return None

def node_view_lookup(label):
    ''' take a string representation of a view function and return ref to that
        function'''
    lookup_table = {
        'task': view_task,
        'concept': view_concept,
        'disorder': view_disorder,
        'behavior': view_behavior,
        'trait': view_trait,
        'theory': view_theory,
        'battery': view_battery,
    }
    try:
        return lookup_table[label]
    except KeyError:
        return None
