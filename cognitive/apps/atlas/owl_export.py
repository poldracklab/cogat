""" Functions to export from api to RDF file

Builds an rdflib graph by crawling list and detail api views for tasks and 
concepts. *_fields dfinitions at top of the file determie what information 
is pulled from a given entry to put into graph. Slower than accessing the db 
directly this will hopefully allow owl exports to work if db representation 
changes but api compatability is maintained. Also allows this to be run by any
user remotely.

"""
import requests
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.extras.infixowl import Class, Restriction, Property
from rdflib.namespace import RDF, RDFS, OWL, FOAF, SKOS, DC

base_url = ""

OBO_REL = Namespace("http://purl.org/obo/owl/OBO_REL#")
SNAP = Namespace("http://www.ifomis.org/bfo/1.1/snap#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
RO = Namespace("https://raw.githubusercontent.com/oborel/obo-relations/master/ro.owl")
# owl = Namespace("http://www.w3.org/2002/07/owl#")
SPAN = Namespace("http://www.ifomis.org/bfo/1.1/span#")
# COGPO = Namespace("http://www.cogpo.org/ontologies/working/CogPOver2011.owl#")
COGPO = Namespace("http://www.cogpo.org/ontologies/CogPOver1.owl")


concept_fields = [
    (DC.Title, 'name'),
    (DC.Contributor, 'def_id_user'),
    (DC.Date, 'creation_time'),
    (SKOS.definition, 'definition_text'),
    (SKOS.prefLabel, 'name'),
    (SKOS.altLabel, 'alias'),
]

concept_class_fields = [
    (DC.Date, 'creation_time'),
    (SKOS.definition, 'description'),
    (DC.Title, 'name'),
    (SKOS.prefLabel, 'name')
]

task_fields = [
    (RDFS.label, 'name'),
    (DC.identifier, 'id'),
    (DC.Title, 'name'),
    (DC.date, 'creation_time'),
    (DC.Contributor, 'def_id_user'),
    (SKOS.definition, 'definition_text'),
    (SKOS.prefLabel, 'name'),
    (SKOS.altLabel, 'alias')
]

contrast_fields = [
    (RDFS.label, 'name'),
    (DC.identifier, 'id'),
    (DC.Title, 'name'),
    (DC.date, 'creation_time'),
    (SKOS.prefLabel, 'name')
]

condition_fields = [
    (RDFS.label, 'name'),
    (DC.identifier, 'id'),
    (DC.Title, 'name'),
    (DC.date, 'creation_time'),
    (SKOS.prefLabel, 'name'),
    (SKOS.definition, 'condition_description')
]


def add_item(item, fields, graph, id='id'):
    ''' Generic function to add individuals from json api.
    
    Args:
        item: json object from cognitive atlas api
        fields: List of tuples with first term being a valid rdflib predicate 
            and the second being a string to use as the object
        graph: rdflib graph to add objects to.
        id: field to pull unique id from item with
    '''
    
    ref = URIRef('#' + item[id])
    if (ref, None, None) in graph:
        # We've already added this ref, bail on adding it again
        return

    graph.add((ref, RDF.type, OWL.Class))
    for field in fields:
        try:
            if item[field[1]] == '':
                print(ref + ' ' + field[1] + ' is empty')
                continue
            graph.add((ref, field[0], Literal(item[field[1]])))
        except KeyError as e:
            print(ref + ' doesnt have ' + field[1])


def add_concepts_to_graph(graph):
    concept_request = requests.get(base_url + 'api/concept')
    concept_json = concept_request.json()
    for concept in concept_json:
        concept_detail = requests.get(base_url + 'concept/json/' + concept['id'] +  '/')
        concept_detail_json = concept_detail.json()
        print("adding" + concept['id'])
        add_item(concept_detail_json, concept_fields, graph)
        ref = URIRef('#' + concept_detail_json['id'])
        for concept_class in concept_detail_json.get('conceptclasses', []):
            cc_ref = '#' + concept_class['id']
            add_item(concept_class, concept_class_fields, graph)
            graph.add((ref, SKOS.hasTopConcept, URIRef(cc_ref)))

        for elem in concept_detail_json.get('concepts', []):
            if elem['relationship'] == 'KINDOF':
                onProperty = RO.kind_of
            elif elem['relationship'] == 'PARTOF':
                onProperty = RO.part_of
            else:
                continue
            sc  = BNode()
            graph.add((ref, RDFS.subClassOf, sc))
            Restriction(onProperty, graph, someValuesFrom=URIRef(elem['id']), identifier=sc)

        for x in [('contrasts', COGPO.has_contrast, contrast_fields)]:
            for elem in concept_detail_json.get(x[0], []):
                add_item(elem, x[2], graph)
                Restriction(x[1], graph, someValuesFrom=URIRef(elem['id']), identifier=sc)

def add_tasks_to_graph(graph):
    tasks_request = requests.get(base_url + 'api/task')
    tasks_json = tasks_request.json()
    for task in tasks_json:
        task_detail_req = requests.get(base_url + 'task/json/'+ task['id'] + '/')
        task_detail_json = task_detail_req.json()
        add_item(task_detail_json, task_fields, graph)
        relations_to_add = [
            ('conditions', RO.has_part, condition_fields), 
            ('contrasts', COGPO.has_contrast, contrast_fields)
        ]
        for x in relations_to_add:
            for elem in task_detail_json.get(x[0], []):
                add_item(elem, x[2], graph)
                Restriction(x[1], graph=graph, someValuesFrom=URIRef('#' + elem['id']))

def build_graph():
    graph = rdflib.Graph()

    # on export uses this string instead of generic ns1, ns2, etc
    graph.bind("owl", OWL)
    graph.bind("dc", DC)
    graph.bind("ro", RO)
    graph.bind("obo", OBO)
    graph.bind("cogpo", COGPO)
    graph.bind("skos", SKOS)


    Property(RO.has_part, graph=graph)

    mb = URIRef('#measured_by') 
    Property(mb, graph=graph)
    graph.add((mb, RDFS.label, Literal('measured_by')))
    iao_desc = '''
        The relationship between a mental concept and a measurement that is 
        thought to reflect the activity of that mental concept.
        '''
    graph.add((mb, OBO.IAO_0000115, Literal(iao_desc)))
    graph.add((mb, RDFS.range, COGPO.COGPO_00049))

    df = URIRef('#descended_from')
    Property(df, graph=graph)
    graph.add((df, RDFS.label, Literal('measured_by')))
    iao_desc = '''
        The relationship between a task and another task of which the former is an
        adaptation.
        '''
    graph.add((df, OBO.IAO_0000115, Literal(iao_desc)))
    graph.add((df, RDFS.range, COGPO.COGPO_00049))


    # properties = properties + '<owl:Class rdf:about="&cogat;CAO_00001">\n\t<rdfs:subClassOf rdf:resource="&skos;Concept"/>\n</owl:Class>\n\n'
    concept = Class(URIRef('Concept'), [ SKOS.Concept ], graph=graph)

    add_tasks_to_graph(graph)
    add_concepts_to_graph(graph)
    return graph

def export_to_owl(path, format="pretty-xml"):
    graph = build_graph()
    graph.serialize(path, format="pretty-xml")

if __name__ == '__main__':
    export_to_owl('./test.rdf')
