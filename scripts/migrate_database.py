# migrate_database.py: Migrate dumps of the Cognitive Atlas database into Neo4j
# see russ_ubergraph.pdf and quasi models below
import os
import re
import pandas
import numpy as np

from py2neo import Graph, Path, Node, Relationship, authenticate

from cognitiveatlas.api import get_task, get_concept

# Function to clean up column names
# Note that Cognitive Atlas exports tables with different header delimiter than rest, I fixed this for
# the data below so all delims are ";"


def cleancolumns(df):
    df.columns = [x.strip() for x in df.columns]
    df = df.replace(np.nan, 'None', regex=True)
    return df

# Function to make a node


def make_node(nodetype, uid, name, properties=None, property_key="id"):
    node = None
    if graph.find_one(nodetype, property_key='id', property_value=uid) is None:
        print("Creating %s:%s, %s" % (nodetype, name, uid))
        timestamp = graph.cypher.execute("RETURN timestamp()").one
        node = Node(
            str(nodetype),
            name=str(name),
            id=str(uid),
            creation_time=timestamp,
            last_updated=timestamp)
        graph.create(node)
        if properties is not None:
            for property_name in properties.keys():
                if properties[property_name]:
                    node.properties[property_name] = properties[property_name]
                else:
                    node.properties[property_name] = "None"

            node.push()
    return node

# Function to make a relation


def make_relation(startnode, rel_type, endnode, properties=None):
    relation = None
    if graph.match_one(
            start_node=startnode,
            rel_type=rel_type,
            end_node=endnode) is None:
        relation = Relationship(startnode, rel_type, endnode)
        print(
            "Creating relation %s [%s] %s" %
            (startnode.properties["name"],
             rel_type,
             endnode.properties["name"]))
        graph.create(relation)
        if properties is not None:
            for property_name in properties.keys():
                relation.properties[property_name] = properties[property_name]
            relation.push()
    return relation


# Function to look up node - return None if doesn't exist
def find_node(nodetype, property_value, property_key='id'):
    try:
        node = graph.find_one(
            nodetype,
            property_key='id',
            property_value=property_value)
    except BaseException:
        node = None
    return node


# First we want to read in all of our data types
search_dir = "scripts/data/"
files = [os.path.join(search_dir, x)
         for x in os.listdir(search_dir)
         if os.path.isfile(os.path.join(search_dir, x))]

concept_files = [x for x in files if 'concept' in x]
concept_files.sort(key=os.path.getmtime)
  
concepts = cleancolumns(pandas.read_csv(concept_files[-1], sep=";"))

task_files = [x for x in files if 'task' in x]
task_files.sort(key=os.path.getmtime)
tasks = cleancolumns(pandas.read_csv(task_files[-1], sep=";"))

contrast_files = [x for x in files if 'contrast' in x]
contrast_files.sort(key=os.path.getmtime)
contrasts = cleancolumns(pandas.read_csv(contrast_files[-1], sep=";"))

battery_files = [x for x in files if 'battery' in x]
battery_files.sort(key=os.path.getmtime)
batteries = cleancolumns(pandas.read_csv(battery_files[-1], sep=";"))

conditions_files = [x for x in files if 'condition' in x]
conditions_files.sort(key=os.path.getmtime)
conditions = cleancolumns(pandas.read_csv(conditions_files[-1], sep=";"))

#disorder_files = [x for x in files if 'disorder' in x]
#disorder_files.sort(key=os.path.getmtime)
#disorders = cleancolumns(pandas.read_csv(disorder_files[-1], sep=";"))

assertion_files = [x for x in files if 'assertion' in x]
assertion_files.sort(key=os.path.getmtime)
assertions = cleancolumns(pandas.read_csv(assertion_files[-1], sep=";"))

theory_files = [x for x in files if 'theory' in x]
theory_files.sort(key=os.path.getmtime)
theories = cleancolumns(pandas.read_csv(theory_files[-1], sep=";"))

# connect to graph database
graph = Graph("http://graphdb:7474/db/data/")

# Just for local development
#authenticate("localhost:7474", "neo4j", "noodles")
#graph = Graph()

# clear database
graph.delete_all()

tx = graph.cypher.begin()

# class Task(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    derived_from = models.Relationship('self',rel_type='DERIVEDFROM')
#    definition = models.StringProperty()
#    has_condition = models.Relationship(Condition,rel_type='HASCONDITION')
#    has_implementation = models.Relationship(Experiment,rel_type='HASIMPLEMENTATION') # ExperimentFactory?
#    mentioned_in = models.Relationship('PMID',rel_type='MENTIONEDIN')

for row in tasks.iterrows():
    name = row[1].term
    uid = row[1].url.split("/")[-1]
    try:
        task = get_task(id=uid, silent=True).json
        definition = task[0]["definition_text"]
    except BaseException:
        definition = ""
    if not str(name) == "nan":
        properties = {"definition": definition}
        node = make_node("task", uid, name, properties)

# class Condition(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    has_contrast = models.Relationship(Contrast,rel_type='HASCONTRAST')

for row in conditions.iterrows():
    name = row[1].condition_text
    user = row[1].id_user
    uid = row[1].id
    task = row[1].id_term
    description = row[1].condition_description
    timestamp = row[1].event_stamp
    if not str(name) == "nan":
        properties = {"condition_description": description, "event_stamp": timestamp, "id_user": user, "codnition_text": name}
        node = make_node("condition", uid, name, properties)
        tasknode = find_node("task", property_value=task)
        # If the tasknode is node found, then we do not create the relation,
        # and we delete the condition
        if tasknode is None:
            graph.delete(node)
        else:
            relation = make_relation(tasknode, "HASCONDITION", node)


# class Disorder(models.NodeModel):
#    has_difference = models.Relationship(Contrast,rel_type='HASDIFFERENCE')
#    mentioned_in = models.Relationship('PMID',rel_type='MENTIONEDIN')

# Bug in returning column index name
#disorders.columns = ["id", "term", "classification"]
#for row in disorders.iterrows():
#    uid = row[1].id
#    classification = row[1].classification
#    name = row[1].term
#    properties = {"classification": classification, "id": id, "term": term}
#    node = make_node("disorder", uid, name, properties)

# class Concept(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    definition = models.StringProperty()
#    related_to = models.Relationship('self',rel_type='RELATEDTO')
#    part_of = models.Relationship('self',rel_type='PARTOF')
#    is_a = models.Relationship('self',rel_type='ISA')
#    measured_by = models.Relationship(Contrast,rel_type='MEASUREDBY')
#    mentioned_in = models.Relationship('PMID',rel_type='MENTIONEDIN')

for row in concepts.iterrows():
    uid = row[1].url.split("/")[-1]
    name = row[1].term
    try:
        concept = get_concept(id=uid, silent=True).json
        definition = concept[0]["definition_text"]
    except BaseException:
        definition = ""
    properties = {"definition": definition}
    node = make_node("concept", uid, name, properties)


# class Contrast(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    measured_by_phenomenon = models.Relationship(Phenomenon,rel_type='MEASUREDBYPHENOMENON')
#    measured_by_trait = models.Relationship(Trait,rel_type='MEASUREDBYTRAIT')

for row in contrasts.iterrows():
    uid = row[1].id
    user = row[1].id_user
    name = row[1].contrast_text
    id_term = row[1].id_term
    timestamp = row[1].event_stamp
    node = make_node("contrast", uid, name,
                     {'id_user': user, 'contrast_text': name,
                      'event_stamp': timestamp, 'event_uri': ''})

    # id_term in the database dumps appears to point at a task, where should
    # that relation be mapped?
    term_node = find_node("task", property_key='id', property_value=id_term)
    if term_node: 
        make_relation(term_node, "HASCONTRAST", node)

    for condition in conditions.iterrows():
        if id_term == condition[1].id_term:
            condition_node = find_node(
                "condition", property_value=condition[1].id)
            if condition_node is not None:
                make_relation(condition_node, "HASCONTRAST", node)

# Assertions!
# We will store the old uid as a property, in case we need to map back to
# original data

for row in assertions.iterrows():
    uid = row[1].id
    user = row[1].id_user
    subject = row[1].id_subject
    relation = row[1].id_relation
    id_type = row[1].id_type
    predicate = row[1].id_predicate
    confidence_level = row[1].confidence_level  # Not sure this was useful
    description = row[1].text_description
    timestamp = row[1].event_stamp
    id_subject_def = row[1].id_subject_def
    id_predicate_def = row[1].id_predicate_def
    # truth_value = row[1].truth_value # I don't know what this is
    # I am not including "flag for curator" because that wasn't very useful
    properties = {"user_id": user, "id": uid}

    # Don't add properties that aren't defined
    if str(confidence_level) != "nan":
        properties["confidence"] = confidence_level
    if str(description) != "nan":
        properties["description"] = description
    if str(timestamp) != "nan":
        properties["timestamp"] = timestamp

    if id_type == "concept-task":
        tasknode = find_node("task", property_value=predicate)
        conceptnode = find_node("concept", property_value=subject)
        contrastnode = find_node("contrast", property_value=id_predicate_def)

        # Contrast is measured by contrast
        if contrastnode is not None and conceptnode is not None:
            relation = make_relation(
                conceptnode, "MEASUREDBY", contrastnode, properties)

        if tasknode and conceptnode:
            make_relation(tasknode, "ASSERTS", conceptnode)
        # We do not model task --> contrast, this comes by way of conditions
        # (task --> conditions --> contrasts)

    elif id_type == "concept-concept":
        conceptnode1 = find_node("concept", property_value=subject)
        conceptnode2 = find_node("concept", property_value=predicate)

        # Figure out relationship type
        if re.search("is a part of", description):
            relationship_type = "PARTOF"
        elif re.search("is a kind of", description):
            relationship_type = "KINDOF"

        # Contrast is measured by contrast
        if conceptnode1 and conceptnode2:
            relation = make_relation(
                conceptnode1, relationship_type, conceptnode2)

    elif id_type == "task-task":
        tasknode1 = find_node("task", property_value=subject)
        tasknode2 = find_node("task", property_value=predicate)

        # Task is descended from task
        if tasknode1 and tasknode2:
            relation = make_relation(tasknode1, "DERIVEDFROM", tasknode2)


# class Battery(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    collection = models.StringProperty()

for row in batteries.iterrows():
    name = row[1].id
    uid = row[1].alias.split("/")[-1]
    battery = row[1].battery
    properties = {"collection": battery}
    node = make_node("battery", uid, name, properties)


# class Theory(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
#    battery = models.StringProperty()

for row in theories.iterrows():
    name = row[1].id
    uid = row[1].alias.split("/")[-1]
    node = make_node("theory", uid, name)


# The following do not exist
# class Trait(models.aNodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)

# class Phenomenon(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)

# class Experiment(models.NodeModel):
#    name = models.StringProperty()
#    uid = models.StringProperty(indexed=True)
