from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from cognitive.settings import graph
import cognitive.apps.atlas.query as query
from .forms import (TaskForm, ConceptForm, ContrastForm, ConditionForm,
                    DisorderForm, TaskDisorderForm)

Assertion = query.Assertion()
Battery = query.Battery()
Citation = query.Citation()
Concept = query.Concept()
Condition = query.Condition()
Contrast = query.Contrast()
Disorder = query.Disorder()
ExternalDataset = query.ExternalDataset()
ExternalLink = query.ExternalLink()
Implementation = query.Implementation()
Indicator = query.Indicator()
Task = query.Task()
Theory = query.Theory()


class NodeAPI(APIView):
    node_class = ...
    form_class = ...
    name_field = ...

    def post(self, request, format=None):
        form = self.form_class(request.data)
        if not form.is_valid():
            return Response(form.errors,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        node_data = form.cleaned_data

        name_exists = self.node_class.get(node_data[self.name_field],
                                          field=self.name_field,
                                          get_relations=False)
        if len(name_exists) > 1:
            error_key = "Name {} already exists".format(
                node_data[self.name_field])
            error_value = "nodes with this name: {}".format(
                [i['id'] for i in name_exists])
            error = {error_key: error_value}
            return Response(error, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        name = node_data[self.name_field]
        node = self.node_class.create(name=name, properties=node_data,
                                      request=request)
        request.GET = request.GET.copy()
        request.GET['id'] = node.properties['id']
        return self.get(request)

    def get(self, request, format=None):
        id = request.GET.get('id', None)
        if id:
            return Response(self.node_class.get_full(request.GET['id'], 'id'))
        else:
            return Response(self.node_class.api_all())

    def make_link(self, request, src_id, src_label, dest_id, dest_label, rel,
                  reverse=False):
        if reverse is False:
            link_made = src_label.link(src_id, dest_id, rel,
                                       endnode_type=dest_label.name)
        elif reverse is True:
            link_made = dest_label.link(dest_id, src_id,
                                        rel, endnode_type=src_label.name)

        if link_made is False:
            return Response({'Unable to associate nodes': ''},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        request.GET = request.GET.copy()
        if reverse is False:
            request.GET['id'] = src_id
        elif reverse is True:
            request.GET['id'] = dest_id

        return self.get(request)


class ContrastAPI(NodeAPI):
    node_class = Contrast
    form_class = ContrastForm
    name_field = 'name'

    def post(self, request, uid, format=None):
        ret = super(ContrastAPI, self).post(request, format=format)
        id = ret.data['id']
        return self.make_link(request, uid, Task, id,
                              Contrast, 'HASCONTRAST')


class ConditionAPI(NodeAPI):
    node_class = Condition
    form_class = ConditionForm
    name_field = 'condition_text'

    def post(self, request, format=None):
        ret = super(ConditionAPI, self).post(request, format=format)
        id = ret.data['id']
        return self.make_link(request, self.kwargs['uid'], Task, id,
                              Condition, 'HASCONDITION')


class ConceptAPI(NodeAPI):
    node_class = Concept
    form_class = ConceptForm
    name_field = 'term_name'

    def get(self, request, format=None):
        fields = {}
        id = request.GET.get("id", "")
        name = request.GET.get("name", "")
        contrast_id = request.GET.get("contrast_id", "")
        if id:
            concept = Concept.get_full(id, 'id')
        elif name:
            concept = Concept.get_full(name, 'name')
        elif contrast_id:
            concept = Contrast.api_get_concepts(contrast_id)
        else:
            concept = Concept.api_all()

        if concept is None:
            raise NotFound('Concept not found')
        return Response(concept)


class TaskAPI(NodeAPI):
    node_class = Task
    form_class = TaskForm
    name_field = 'term_name'

    def get(self, request, format=None):
        id = request.GET.get("id", "")
        name = request.GET.get("name", "")

        if id:
            task = Task.get_full(id, 'id')
        elif name:
            task = Task.get_full(name, 'name')
        else:
            task = Task.api_all()

        if task is None:
            raise NotFound('Task not found')
        return Response(task)


class DisorderAPI(NodeAPI):
    node_class = Disorder
    form_class = DisorderForm
    name_field = 'name'

    def get(self, request, format=None):
        id = request.GET.get("id", "")
        name = request.GET.get("name", "")

        if id:
            disorder = Disorder.get_full(id, 'id')
        elif name:
            disorder = Disorder.get_full(name, 'name')
        else:
            disorder = Disorder.api_all()

        if disorder is None:
            raise NotFound('Disorder not found')
        return Response(disorder)


class SearchAPI(APIView):
    def get(self, request, format=None):
        search_classes = [Concept, Contrast, Disorder, Task]
        queries = request.GET.get("q", "")
        results = []
        for sclass in search_classes:
            result = sclass.search_all_fields(queries)
            results += result
        if not results:
            raise NotFound('No results found')
        return Response(results)

# def add_concept_relation(request, uid):
# def make_link(self, request, src_id, src_label, dest_id, dest_label, rel,


class ConceptRelAPI(NodeAPI):
    node_class = Concept
    form_class = None
    name_field = None

    def post(self, request):
        # Need some sort of validation.
        src_id = request.POST.get('src_id', None)
        dest_id = request.POST.get('dest_id', None)
        rel_type = request.POST.get('rel_type', None)
        return self.make_link(request, src_id, self.node_class, dest_id,
                              self.node_class, rel_type)

# def all_batteries(request):
# def all_theories(request):
# def all_collections(request, return_context=False):
# def all_disorders(request, return_context=False):
# def all_contrasts(request):
# def view_battery(request, uid, return_context=False):
# handled in battery class
# def view_theory(request, uid, return_context=False):
# handled in theory class

# def update_concept(request, uid):
# def update_task(request, uid):
# def update_theory(request, uid):
# def update_battery(request, uid):
# def update_disorder(request, uid):

# def add_task_concept(request, uid):


class TaskConceptAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        concept_id = request.POST.get('concept_id', '')
        return self.make_link(request, uid, self.node_class,
                              concept_id, Concept, 'ASSERTS')

# def add_disorder_task(request, uid):


class DisorderTask(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        disorder_id = request.POST.get('disorder_id', '')
        return self.make_link(request, uid, self.node_class,
                              disorder_id, Disorder, 'ASSERTS')


# def add_task_disorder(request, task_id):
class TaskDisorderAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        form = TaskDisorderForm(uid, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            disorder_id = cleaned_data['disorders']
            cont_id = cleaned_data['contrasts']
            Contrast.link(cont_id, disorder_id, "HASDIFFERENCE",
                          endnode_type="disorder")
            request.GET = request.GET.copy()
            request.GET['id'] = uid
            return self.get(request)
        else:
            return Response(form.errors,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# def add_disorder_disorder(request, disorder_id):


class DisorderDisorderAPI(NodeAPI):
    node_class = Disorder

    def post(self, request, uid):
        disorder_id = request.POST.get('disorder_id', '')
        return self.make_link(request, uid, self.node_class,
                              disorder_id, Disorder, 'ISA')

# def add_concept_contrast(request, uid, tid):


class ConceptContrastAPI(NodeAPI):
    pass
# def add_concept_contrast_task(request, uid):


class ConceptContrastTaskAPI(NodeAPI):
    pass
# def concept_task_contrast_assertion(concept_id, task_id, contrast_id):

# def add_task_implementation(request, task_id):


class TaskImplementationAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        imp_id = request.POST.get('implementation_id', '')
        return self.make_link(request, uid, self.node_class, dataset_id,
                              Implementation, 'HASIMPLEMENTATION')

# def add_task_dataset(request, task_id):


class TaskDatasetAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        dataset_id = request.POST.get('dataset_id', '')
        return self.make_link(request, uid, self.node_class, dataset_id,
                              ExternalDataset, 'HASEXTERNALDATASET')

# def add_task_indicator(request, task_id):


class TaskIndicatorAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        indicator_id = request.POST.get('indicator_id', '')
        return self.make_link(request, uid, self.node_class, indicator_id,
                              Indicator, 'HASINDICATOR')

# def add_task_citation(request, task_id):


class TaskCitationAPI(NodeAPI):
    node_class = Task

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_concept_citation(request, concept_id):


class ConceptCitationAPI(NodeAPI):
    node_class = Concept

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_disorder_citation(request, disorder_id):


class DisorderCitationAPI(NodeAPI):
    node_class = Disorder

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_disorder_external_link(request, disorder_id):


class DisorderExternalLinkAPI(NodeAPI):
    node_class = Disorder

    def post(self, request, uid):
        link_id = request.POST.get('link_id', '')
        return self.make_link(request, uid, self.node_class, link_id,
                              ExternalLink, 'HASLINK')

# def add_theory_citation(request, theory_id):


class TheoryCitationAPI(NodeAPI):
    node_class = Theory

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_battery_citation(request, battery_id):


class BatteryCitationAPI(NodeAPI):
    node_class = Battery

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_battery_indicator(request, battery_id):


class BatteryIndicatorAPI(NodeAPI):
    node_class = Battery

    def post(self, request, uid):
        citation_id = request.POST.get('citation_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Citation, 'HASCITATION')

# def add_battery_battery(request, battery_id):


class BatteryBatteryAPI(NodeAPI):
    node_class = Battery

    def post(self, request, uid):
        battery_id = request.POST.get('battery_id', '')
        return self.make_link(request, uid, self.node_class, citation_id,
                              Battery, 'INBATTERY')

# def add_battery_task(request, battery_id):


class BatteryTaskAPI(NodeAPI):
    node_class = Battery

    def post(self, request, uid):
        task_id = request.POST.get('task_id', '')
        return self.make_link(request, uid, self.node_class, task_id,
                              Task, 'INBATTERY')

# def add_theory_assertion(request, theory_id):


class TheoryAssertion(NodeAPI):
    node_class = Assertion

    def post(self, request, uid):
        theory_id = request.POST.get('theory_id', '')
        return self.make_link(request, uid, self.node_class, theory_id,
                              Theory, 'INTHEORY')
# def add_theory(request):


class TheoryAPI(NodeAPI):
    node_class = Theory

# def add_battery(request):


class BatteryAPI(NodeAPI):
    node_class = Battery
