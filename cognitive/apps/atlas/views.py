''' Functional views to create, update, and view the various types of terms
    and their relationships in cognitive atlas. '''
import json

from py2neo import Graph, Node, Relationship

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import redirect, render


from cognitive.apps.atlas.forms import (CitationForm, DisorderForm,
                                        ExternalDatasetForm,
                                        ImplementationForm, IndicatorForm,
                                        TaskDisorderForm, TheoryAssertionForm,
                                        TheoryForm, BatteryForm,
                                        ConceptTaskForm, ConceptContrastForm,
                                        DisorderDisorderForm, ExternalLinkForm)

from cognitive.apps.atlas.query import (Assertion, Concept, Task, Disorder,
                                        Contrast, Battery, Theory, Condition,
                                        Implementation, Indicator,
                                        ExternalDataset, Citation, ExternalLink,
                                        search)
from cognitive.apps.atlas.utils import clean_html, update_lookup, add_update
from cognitive.settings import DOMAIN, graph

Assertion = Assertion()
Battery = Battery()
Citation = Citation()
Concept = Concept()
Condition = Condition()
Contrast = Contrast()
Disorder = Disorder()
ExternalDataset = ExternalDataset()
ExternalLink = ExternalLink()
Implementation = Implementation()
Indicator = Indicator()
Task = Task()
Theory = Theory()

# Needed on all pages
counts = {
    "disorders": Disorder.count(),
    "tasks": Task.count(),
    "contrasts": Contrast.count(),
    "concepts": Concept.count(),
    "collections": (Battery.count() + Theory.count()),
}

# VIEWS FOR ALL NODES #############################################################

def all_nodes(request, nodes, node_type, node_type_plural):
    '''all_nodes returns view with all nodes for node_type'''

    context = {
        'term_type': node_type,
        'term_type_plural': node_type_plural,
        'nodes': nodes,
        'filtered_nodes_count': counts[node_type_plural],
        'counts': counts
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
        'counts': counts,
        'theory_form': TheoryForm(),
        'battery_form': BatteryForm()
    }
    if return_context:
        return context

    return render(request, "atlas/all_collections.html", context)


def disorder_populate(disorders):
    ret = {}
    for dis in disorders:
        key = (str(dis.properties['id']), str(dis.properties['name']))
        ret[key] = disorder_populate([x.start_node for x in dis.match_incoming(rel_type="ISA")])
    return ret

def all_disorders(request, return_context=False):
    '''all_disorders returns page with list of all disorders'''
    disorder_form = DisorderForm

    dis_records = graph.cypher.execute(
        "match (dis:disorder) where not (dis:disorder)-[:ISA]->() return dis order by dis.name"
    )
    top_level_disorders = [x['dis'] for x in dis_records]
    disorders = disorder_populate(top_level_disorders)

    context = {
        'appname': "The Cognitive Atlas",
        'active': "disorders",
        'disorder_form': disorder_form,
        'disorders': disorders
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
        'filtered_nodes_count': nodes_count
    }

    return render(request, "atlas/terms_by_letter.html", context)

def concepts_by_letter(request, letter):
    '''concepts_by_letter returns concept view for a certain letter'''
    concepts = Concept.filter(filters=[("name", "starts_with", letter)])
    concepts_count = len(concepts)
    return nodes_by_letter(request, letter, concepts, concepts_count, "concepts")

def tasks_by_letter(request, letter):
    '''tasks_by_letter returns task view for a certain letter'''
    tasks = Task.filter(filters=[("name", "starts_with", letter)])
    tasks_count = len(tasks)
    return nodes_by_letter(request, letter, tasks, tasks_count, "tasks")


# VIEWS FOR SINGLE NODES ##########################################################

def view_concept(request, uid):
    concept = Concept.get(uid)[0]

    # For each measured by (contrast), get the task
    if "MEASUREDBY" in concept["relations"]:
        for c in range(len(concept["relations"]["MEASUREDBY"])):
            contrast = concept["relations"]["MEASUREDBY"][c]
            tasks = Contrast.get_tasks(contrast["id"])
            concept["relations"]["MEASUREDBY"][c]["tasks"] = tasks

    citations = Concept.get_relation(concept["id"], "HASCITATION")
    tasks = Concept.get_reverse_relation(concept["id"], "ASSERTS")
    contrasts = Concept.get_relation(concept["id"], "MEASUREDBY")

    assertions = []
    assertions_no_cont = []
    for task in tasks:
        task_contrasts = Task.get_relation(task["id"], "HASCONTRAST")
        return_contrasts = []
        for task_contrast in task_contrasts:
            for contrast in contrasts:
                if task_contrast["id"] == contrast["id"]:
                    return_contrasts.append(task_contrast)
        if return_contrasts:
            assertions.append((task, return_contrasts))
        else:
            assertions_no_cont.append((task, ConceptContrastForm(task["id"],
                                                                 uid)))

    are_kinds_of = Concept.get_reverse_relation(concept["id"], "KINDOF")
    are_parts_of = Concept.get_reverse_relation(concept["id"], "PARTOF")

    context = {
        "are_kinds_of": are_kinds_of,
        "are_parts_of": are_parts_of,
        "concept": concept,
        "assertions": assertions,
        "assertions_no_cont": assertions_no_cont,
        "citations": citations,
        "citation_form": CitationForm(),
        "concept_task_form": ConceptTaskForm()
    }

    return render(request, 'atlas/view_concept.html', context)


def view_task(request, uid, return_context=False):
    try:
        task = Task.get(uid)[0]
    except IndexError:
        return HttpResponseNotFound('<h1>Task with uid {} not found.</h1>'.format(uid))

    # Replace newlines with <br>, etc.
    task["definition"] = clean_html(task.get("definition", "No definition provided"))
    contrasts = Task.api_get_contrasts(task["id"])

    concept_lookup = dict()

    # Retrieve conditions, make associations with contrasts
    conditions = Task.get_conditions(task["id"])

    implementations = Task.get_relation(task["id"], "HASIMPLEMENTATION")
    datasets = Task.get_relation(task["id"], "HASEXTERNALDATASET")
    indicators = Task.get_relation(task["id"], "HASINDICATOR")
    citations = Task.get_relation(task["id"], "HASCITATION")
    disorders = Task.get_relation(task["id"], "ASSERTS")

    context = {
        "task": task,
        "concepts": concept_lookup,
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
        "citation_form": CitationForm(),
        "disorders": disorders,
        "task_disorder_form": TaskDisorderForm(uid),
    }

    if return_context is True:
        return context
    return render(request, 'atlas/view_task.html', context)

def view_battery(request, uid, return_context=False):
    ''' detail view for a battery. '''
    battery = Battery.get(uid)[0]
    progenitors = Battery.get_relation(uid, "PARTOF")
    descendants = Battery.get_reverse_relation(uid, "PARTOF")
    indicators = Battery.get_relation(uid, "HASINDICATOR")
    constituent_tasks = Battery.get_relation(uid, "INBATTERY")
    citations = Battery.get_relation(uid, "HASCITATION")
    context = {
        "battery": battery,
        "citations": citations,
        "citation_form": CitationForm(),
        "indicators": indicators,
        "indicator_form": IndicatorForm(),
        "progenitors": progenitors,
        "descendants": descendants
    }
    if return_context:
        return context
    return render(request, 'atlas/view_battery.html', context)

def view_theory(request, uid, return_context=False):
    ''' detail view for a given assertion '''
    theory = Theory.get(uid)[0]
    assertions = Theory.get_reverse_relation(uid, "INTHEORY")
    # test if logged in, this might be an expensive operation since choices
    # field is populated on each instantiation
    theory_assertions_form = TheoryAssertionForm()
    citations = Theory.get_relation(uid, "HASCITATION")
    referenced_terms = {}
    for asrt in assertions:
        pred = Assertion.get_relation(asrt['id'], "PREDICATE")[0]
        subj = Assertion.get_relation(asrt['id'], "SUBJECT")[0]
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
        "assertions": assertions,
        "theory_assertions_form": theory_assertions_form,
        "referenced_terms": referenced_terms,
        "citation_form": CitationForm(),
        "citations": citations
    }
    if return_context is True:
        return context
    return render(request, 'atlas/view_theory.html', context)

def view_disorder(request, uid, return_context=False):
    ''' detail view for a given disorder '''
    disorder = Disorder.get(uid)[0]
    assertions = []
    tasks = Disorder.get_reverse_relation(uid, "ASSERTS")
    contrasts = Disorder.get_reverse_relation(uid, "HASDIFFERENCE")
    parent_disorders = Disorder.get_relation(uid, "ISA")
    child_disorders = Disorder.get_reverse_relation(uid, "ISA")
    external_links = Disorder.get_relation(uid, "HASLINK")

    assertions = []
    for task in tasks:
        task_contrasts = Task.get_relation(task["id"], "HASCONTRAST")
        return_contrasts = []
        for task_contrast in task_contrasts:
            for contrast in contrasts:
                if task_contrast["id"] == contrast["id"]:
                    return_contrasts.append(task_contrast)
        assertions.append((task, return_contrasts))

    citations = Disorder.get_relation(disorder["id"], "HASCITATION")
    context = {
        "disorder":disorder,
        "citations": citations,
        "citation_form": CitationForm(),
        "assertions": assertions,
        "disorder_form": DisorderDisorderForm(),
        "parent_disorders": parent_disorders,
        "child_disorders": child_disorders,
        "external_links": external_links,
        "external_link_form": ExternalLinkForm()
    }

    if return_context:
        return context
    return render(request, 'atlas/view_disorder.html', context)


# ADD NEW TERMS ###################################################################

@login_required
def contribute_term(request):
    '''contribute_term will return the contribution detail page for a term that is
    posted, or visiting the page without a POST will return the original form
    '''

    context = {"message":"Please specify the term you want to contribute."}

    if request.method == "POST":
        term_name = request.POST.get('newterm', '')

        # Does the term exist in the atlas?
        results = search(term_name)
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
def contribute_disorder(request):
    ''' contribute_disorder will return the detail page for the new disorder '''
    if request.method == "POST":
        disorder_form = DisorderForm(request.POST)
        if disorder_form.is_valid():
            cleaned_data = disorder_form.cleaned_data
            properties = {"definition": cleaned_data['definition']}
            new_dis = Disorder.create(cleaned_data["name"], properties)
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
def add_term(request):
    '''add_term will add a new term to the atlas
    '''

    if request.method == "POST":
        term_type = request.POST.get('term_type', '')
        term_name = request.POST.get('term_name', '')
        definition_text = request.POST.get('definition_text', '')

        properties = None
        if definition_text != '':
            properties = {"definition":definition_text}

        if term_type == "concept":
            node = Concept.create(name=term_name, properties=properties)
            return redirect('concept', node["id"])

        elif term_type == "task":
            node = Task.create(name=term_name, properties=properties)
            return redirect('task', node["id"])

#def contribute_disorder(request):
#    return render(request, 'atlas/contribute_disorder.html', context)

@login_required
def add_condition(request, task_id):
    '''add_condition will associate a condition with the given task
    :param task_id: the uid of the task, to return to the correct page after creation
    '''
    if request.method == "POST":
        relation_type = "HASCONDITION" #task --HASCONDITION-> condition
        condition_name = request.POST.get('condition_name', '')

        if condition_name != "":
            condition = Condition.create(name=condition_name)
            Task.link(task_id, condition["id"], relation_type, endnode_type="condition")
    return view_task(request, task_id)


# UPDATE TERMS ####################################################################

@login_required
def update_concept(request, uid):
    if request.method == "POST":
        definition = request.POST.get('definition', '')
        updates = add_update("definition", definition)
        Concept.update(uid, updates=updates)
    return view_concept(request, uid)

@login_required
def update_task(request, uid):
    if request.method == "POST":
        definition = request.POST.get('definition', '')
        updates = add_update("definition", definition)
        Task.update(uid, updates=updates)
    return view_task(request, uid)

@login_required
def update_theory(request, uid):
    if request.method == "POST":
        description = request.POST.get('theory_description', '')
        name = request.POST.get('theory_name', '')
        updates = add_update("name", name)
        updates = add_update("description", description, updates)
        Theory.update(uid, updates=updates)
    return view_theory(request, uid)

@login_required
def update_battery(request, uid):
    if request.method == "POST":
        description = request.POST.get('description', '')
        updates = add_update("description", description)
        Battery.update(uid, updates=updates)
    return view_battery(request, uid)


@login_required
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
def add_task_concept(request, uid):
    '''add_task_concept will add a cognitive concept to the list on a
       task page, making the assertion that the concept is associated
       with the task.
    :param uid: the unique id of the task, for returning to the task page when finished
    '''
    if request.method == "POST":
        relation_type = "ASSERTS" #task --asserts-> concept
        concept_selection = request.POST.get('concept_selection', '')
        Task.link(uid, concept_selection, relation_type, endnode_type="concept")
    return view_task(request, uid)

@login_required
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
    print(assertion)
    if assertion.records == []:
        asrt = Assertion.create("")
        Assertion.link(asrt.properties['id'], disorder_id, "SUBJECT", endnode_type='disorder')
        Assertion.link(asrt.properties['id'], task_selection, "PREDICATE", endnode_type='task')

    return redirect('disorder', disorder_id)

def add_disorder_disorder(request, disorder_id):
    ''' process form from disorder view that relates disorders to disorders '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = DisorderDisorderForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        rel_dis_id = cleaned_data['disorders']
        rel_type = cleaned_data['type']
        if rel_type == 'parent':
            rel = Disorder.link(disorder_id, rel_dis_id, "ISA", "disorder")
        else:
            rel = Disorder.link(rel_dis_id, disorder_id, "ISA", "disorder")
        return view_disorder(request, disorder_id)
    else:
        context = view_disorder(request, disorder_id, return_context=True)
        context['disorder_form'] = form
        return render(request, 'atlas/view_disorder.html', context)


    return redirect('disorder', disorder_id)

@login_required
def add_concept_contrast(request, uid, tid):
    ''' process form from concept view to add contrast that measures concept '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = ConceptContrastForm(tid, uid, request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        contrast_id = cleaned_data['contrasts']
        rel = Concept.link(uid, contrast_id, "MEASUREDBY", "contrast")
        concept_task_contrast_assertion(uid, tid, contrast_id)
        return view_concept(request, uid)
    else:
        # would have to insert the form into the assertions_no_contrast list.
        return view_concept(request, uid)

@login_required
def add_concept_contrast_task(request, uid):
    '''add_concept_contrast will add a contrast associated with conditions--> task via the task view
    :param uid: the uid of the task, to return to the correct page after creation
    '''
    if request.method == "POST":
        relation_type = "MEASUREDBY" #concept --MEASUREDBY-> contrast
        contrast_selection = request.POST.get('contrast_selection', '')
        concept_id = request.POST.get('concept_id', '')
        Concept.link(concept_id, contrast_selection, relation_type,
                     endnode_type="contrast")
        concept_task_contrast_assertion(concept_id, uid, contrast_selection)
    return view_task(request, uid)

@login_required
def concept_task_contrast_assertion(concept_id, task_id, contrast_id):
    ''' function to generate assertion node along with all three relations assocaited with it'''
    pass

@login_required
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
            weight = int(request.POST.get(condition_id, 0)[0])
            if weight != 0:
                conditions[condition_id] = weight

        if contrast_name != "" and len(conditions) > 0:
            node = Contrast.create(name=contrast_name)
            # Associate task and contrast so we can look it up for task view
            Task.link(task_id, node.properties["id"], relation_type, endnode_type="contrast")

            # Make a link between contrast and conditions, specify side as property of relation
            for condition_id, weight in conditions.items():
                properties = {"weight":weight}
                Condition.link(condition_id, node["id"], relation_type,
                               endnode_type="contrast", properties=properties)

    return view_task(request, task_id)

@login_required
def add_task_disorder(request, task_id):
    ''' From the task we can create a link between the task we are viewing and
        a disorder.'''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    task_disorder_form = TaskDisorderForm(task_id, request.POST)
    if task_disorder_form.is_valid():
        cleaned_data = task_disorder_form.cleaned_data
        disorder_id = cleaned_data['disorders']
        cont_id = cleaned_data['contrasts']
        Contrast.link(cont_id, disorder_id, "HASDIFFERENCE", endnode_type="disorder")
        return view_task(request, task_id)
    else:
        context = view_task(request, task_id, return_context=True)
        context['task_disorder_form'] = task_disorder_form
        return render(request, 'atlas/view_task.html', context)


@login_required
def make_link(request, src_id, src_label, dest_label, form_class, name_field,
              view, rel):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    form = form_class(request.POST)
    if not form.is_valid():
        return view(request, src_id)
    clean_data = form.cleaned_data
    dest_node = dest_label.create(clean_data[name_field], properties=clean_data)
    if dest_node is None:
        messages.error(request, "Was unable to create {}".format(dest_label.name))
        return view(request, src_id)
    link_made = src_label.link(src_id, dest_node.properties['id'],
                               rel, endnode_type=dest_label.name)
    if link_made is None:
        graph.delete(dest_node)
        error_msg = "Was unable to associate {} and {}".format(
                src_label.name, dest_label.name)
        messages.error(request, error_msg)
    return view(request, src_id)

@login_required
def add_task_implementation(request, task_id):
    ''' From the task view we can create an implementation that is associated
        with a given task'''
    return make_link(request, task_id, Task, Implementation,
                     ImplementationForm, 'implementation_name', view_task,
                     "HASIMPLEMENTATION")

@login_required
def add_task_dataset(request, task_id):
    ''' From the task view we can create a link to dataset that is associated
        with a given task'''
    return make_link(request, task_id, Task, ExternalDataset,
                     ExternalDatasetForm, 'dataset_name', view_task,
                     "HASEXTERNALDATASET")

@login_required
def add_task_indicator(request, task_id):
    ''' From the task view we can create a link to indicator that is associated
        with a given task.'''
    return make_link(request, task_id, Task, Indicator, IndicatorForm, 
                     'type', view_task, "HASINDICATOR")

@login_required
def add_task_citation(request, task_id):
    ''' From the task view we can create a link to citation that is associated
        with a given task.'''
    return make_link(request, task_id, Task, Citation, CitationForm,
                     'citation_desc', view_task, "HASCITATION")

@login_required
def add_concept_citation(request, concept_id):
    ''' From the task view we can create a link to citation that is associated
        with a given task.'''
    return make_link(request, concept_id, Concept, Citation, CitationForm,
                     'citation_desc', view_concept, "HASCITATION")

@login_required
def add_disorder_citation(request, disorder_id):
    ''' From the task view we can create a link to citation that is associated
        with a given task.'''
    return make_link(request, disorder_id, Disorder, Citation, CitationForm,
                     'citation_desc', view_disorder, "HASCITATION")

# need to add ExternalLink to query and make form
@login_required
def add_disorder_external_link(request, disorder_id):
    ''' From the task view we can create a link to citation that is associated
        with a given task.'''
    return make_link(request, disorder_id, Disorder, ExternalLink,
                     ExternalLinkForm, 'uri', view_disorder, "HASLINK")

@login_required
def add_theory_citation(request, theory_id):
    return make_link(request, theory_id, Theory, Citation, CitationForm,
                     'citation_desc', view_theory, "HASCITATION")

@login_required
def add_battery_citation(request, battery_id):
    return make_link(request, battery_id, Battery, Citation, CitationForm,
                     'citation_desc', view_battery, "HASCITATION")

@login_required
def add_battery_indicator(request, battery_id):
    return make_link(request, battery_id, Battery, Indicator, IndicatorForm,
                     'type', view_battery, "HASINDICATOR")


@login_required
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
def add_theory(request):
    ''' from all collections we can add new theories, this view handles that '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    theory_form = TheoryForm(request.POST)
    if theory_form.is_valid():
        cleaned_data = theory_form.cleaned_data
        name = cleaned_data['name']
        new_theory = Theory.create(name)
        return view_theory(request, new_theory.properties['id'])
    else:
        context = all_collections(request, return_context=True)
        context['theory_form'] = theory_form
        return render(request, 'atlas/all_collections.html', context)

@login_required
def add_battery(request):
    ''' from all collections we can add new theories, this view handles that '''
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    battery_form = TheoryForm(request.POST)
    if battery_form.is_valid():
        cleaned_data = battery_form.cleaned_data
        name = cleaned_data['name']
        new_battery = Battery.create(name)
        return view_battery(request, new_battery.properties['id'])
    else:
        context = all_collections(request, return_context=True)
        context['battery_form'] = battery_form
        return render(request, 'atlas/all_collections.html', context)

# SEARCH TERMS ####################################################################

def search_all(request):
    ''' used by templates via ajax when searching for terms '''
    data = "no results"
    search_text = request.POST.get("searchterm", "")
    results = []
    if search_text != '':
        results = search(search_text)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def search_by_type(request, node_type):
    ''' Used by ajax in the templates when adding concepts to a task '''
    data = "no results"
    search_text = request.POST.get("relationterm", "")
    results = []
    if search_text != '':
        results = search(search_text, node_type=node_type)
        data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def search_concept(request):
    ''' Used by ajax in the templates when adding concepts to a task '''
    return search_by_type(request, "concept")

def search_task(request):
    ''' Used by ajax in the templates when adding concepts to a task '''
    return search_by_type(request, "task")
