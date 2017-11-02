''' This file contains classes that are used to query and update the neo4j
    graph.'''
import re

from py2neo import Path, Node as NeoNode, Relationship
import pandas

from cognitive.apps.atlas.utils import (color_by_relation, generate_uid,
                                        do_query, get_relation_nodetype)
import cognitive.settings as settings

class InvalidNodeOperation(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Node(object):

    def __init__(self, name="generic", fields=None, graph=settings.graph):
        '''Node is a general class to represent a neo4j node
        '''
        self.name = name
        self.graph = graph
        self.relations = {"GENERIC": "node"}
        self.color = None
        if fields is None:
            self.fields = ["id", "name"]
        else:
            self.fields = fields

    def count(self):
        '''count returns the count :) I am ze-count! One two three...! one two... three!
        '''
        query = "MATCH (n:{}) RETURN count(*)".format(self.name)
        return self.graph.cypher.execute(query).one


    def create(self, name, properties=None, property_key="id", request=None, unique_name=False, label=None):
        '''create will create a new node of nodetype with unique id uid, and properties
        :param uid: the unique identifier
        :param name: the name of the node
        :param properties: a dictionary of properties with {field:value} for the node
        '''
        if label is None:
            label = self.name
        node = None
        # creation also checks for existence of uid
        uid = generate_uid(label)
        if self.graph.find_one(label, property_key=property_key, property_value=uid) is None:
            timestamp = self.graph.cypher.execute("RETURN timestamp()").one
            node = NeoNode(label, name=name, id=uid, creation_time=timestamp,
                           last_updated=timestamp)
            create_ret = self.graph.create(node)
            if properties != None:
                for property_name in properties.keys():
                    node.properties[property_name] = properties[property_name]
                node.push()
            if request and (len(create_ret) > 0):
                self.log_create(request, uid, label)
        return node

    def neo_user_lookup(self, request):
        ''' see if user from current request exists as a node in the neo
            database. If not make a node for them. These nodes used for basic
            audit of changes made to other nodes.
        '''
        user_id = request.user.id
        neo_user = self.graph.find_one("user", property_key="id",
                                       property_value=user_id)
        user = User()
        if not neo_user:
            user.create(user_id, properties={'username': request.user.username,
                                             'id': user_id})

    def log_create(self, request, node_id, label=None):
        ''' associate user node who created a given node to the newly created
            node
        '''
        if label is None:
            label = self.name

        self.neo_user_lookup(request)
        user = User()
        user.link(request.user.id, node_id, "CREATED", endnode_type=self.name)

    def log_update(self, request, node_id):
        ''' assocaite user who most recently updated a node. If another user
            has this relation set, remove it.
        '''
        self.neo_user_lookup(request)
        user = User()
        query = "MATCH ()-[rel:UPDATED]->(dest) WHERE dest.id = '{}' RETURN rel"
        res = self.graph.cypher.execute(query)
        if res[0]:
            res[0]['rel'].delete()
        user.link(request.user.id, node_id, "UPDATED", endnode_type=self.name)

    def link(self, uid, endnode_id, relation_type, endnode_type=None, properties=None, label=None):
        '''link will create a new link (relation) from a uid to a relation, first confirming
        that the relation is valid for the node
        :param uid: the unique identifier for the source node
        :param endnode_id: the unique identifier for the end node
        :raram relation_type: the relation type
        :param endnode_type: the type of the second node. If not specified, assumed to be
               same as startnode
        :param properties: properties to add to the relation
        '''
        if label is None:
            label = self.name
        if endnode_type is None:
            endnode_type = self.name
        startnode = self.graph.find_one(label, property_key='id', property_value=uid)
        endnode = self.graph.find_one(endnode_type, property_key='id', property_value=endnode_id)

        if startnode != None and endnode != None:
            # If the relation_type is allowed for the node type
            if relation_type not in self.relations:
                raise InvalidNodeOperation("Relationship type not used by this node type")
            if self.graph.match_one(start_node=startnode,
                                    rel_type=relation_type, end_node=endnode) is None:
                relation = Relationship(startnode, relation_type, endnode)
                self.graph.create(relation)
                if properties != None:
                    for property_name in properties.keys():
                        relation.properties[property_name] = properties[property_name]
                    relation.push()
                return relation
        return None

    def unlink(self, uid, endnode_id, relation_type, endnode_type=None):
        ''' attempt to unlink the two nodes specified by the relation specified. '''

        if endnode_type is None:
            endnode_type = self.name

        query = '''
            MATCH (n1:{})-[r:{}]->(n2:{})
            WHERE n1.id = '{}' and n2.id = '{}'
            DELETE r
        '''.format(self.name, relation_type, endnode_type, uid, endnode_id)

        try:
            self.graph.cypher.execute(query)
            return None
        except Exception as e:
            return e


    def update(self, uid, updates, label=None):
        '''update will update a particular field of a node with a new entry
        :param uid: the unique id of the node
        :param updates: a dictionary with {field:value} to update node with
        '''
        if label is None:
            label = self.name
        node = self.graph.find_one(label, 'id', uid)
        if node != None:
            for field, update in updates.items():
                node[field] = update
            node.push()


    def cypher(self, uid, lookup=None, return_lookup=False):
        ''' cypher returns a data structure with nodes and relations for an
            object to generate a gist with cypher
        :param uid: the node unique id to look up
        :param lookup: an optional lookup dictionary to append to
        :param return_lookup: if true, returns a lookup with nodes and relations that are added to the graph
        '''
        base = self.get(uid)[0]

        # Keep track of nodes we've seen
        links = []
        nodes = []

        # Update the lookup
        if lookup is None:
            lookup = dict()
        if self.name not in lookup:
            lookup[self.name] = []
        if base["id"] not in lookup[self.name]:
            lookup[self.name].append(base["id"])
            nodes.append(cypher_node(base["id"], self.name, base["name"], base["_id"]))
            # id is the cognitive atlas id, _id is the graph id

        if "relations" in base:
            for relation_type, relations in base["relations"].items():
                node_type = get_relation_nodetype(relation_type)
                if node_type not in lookup:
                    lookup[node_type] = []
                for relation in relations:
                    if relation["id"] not in lookup[node_type]:
                        lookup[node_type].append(relation["id"])
                        nodes.append(cypher_node(relation["id"], node_type, relation["relationship_type"],
                                                 relation["_id"]))
                        links.append(cypher_relation(relation_type, base["_id"], relation["_id"]))

        result = {"nodes":nodes, "links":links}
        if return_lookup is True:
            return result, lookup
        return result

    def get_graph(self, uid, fields=None):
        '''graph returns a graph representation of one or more nodes, meaning a dictionary of nodes/links with
        (minimally) fields name, label, and id. Additional fields are included that are defined in the Node
        objects fields. THIS FUNCTION WILL LIKELY BE REMOVED.
        '''
        minimum_fields = ["name"]
        if fields is None:
            fields = self.fields
            new_fields = [x for x in fields if x not in minimum_fields]
            minimum_fields = minimum_fields + new_fields

        if isinstance(uid, str):
            uid = [uid]

        nodes = []
        links = []
        lookup = dict()
        count = 1
        for uu in uid:
            entity = self.get(uu)[0]

            # Entity node
            if entity["id"] not in lookup:
                lookup[entity["id"]] = count
                count += 1

            node = {field:entity[field] for field in minimum_fields if field in entity}
            node["label"] = "{}: {}".format(self.name, entity["name"])
            node["color"] = self.color
            node["id"] = lookup[entity["id"]]
            nodes.append(node)

            # Relations
            if "relations" in entity:
                for relation_name, relations in entity["relations"].items():
                    for relation in relations:
                        if relation["id"] not in lookup:
                            lookup[relation["id"]] = count
                            count += 1

                        node = {field:relation[field] for field in minimum_fields if field in relation}
                        node["label"] = "{}: {}".format(relation_name, relation["name"])
                        node["id"] = lookup[relation["id"]]
                        node["color"] = color_by_relation(relation_name)
                        link = {
                            "source": lookup[entity["id"]],
                            "target": lookup[relation["id"]],
                            "type": relation_name
                        }
                        links.append(link)
                        nodes.append(node)

        result = {
            "nodes": nodes,
            "links": links
        }
        return result


    def filter(self, filters, format="dict", fields=None):
        '''filter will filter a node based on some set of filters
        :param filters: a list of tuples with [(field,filter,value)],
                        eg [("name","starts_with","a")].
        ::note_

             Currently supported filters are "starts_with"
        '''
        if fields is None:
            fields = self.fields
        return_fields = ",".join(["n.%s" %(x) for x in fields] + ["ID(n)"])

        query = "MATCH (n:{})".format(self.name)
        for tup in filters:
            filter_field, filter_name, filter_value = tup
            if filter_name == "starts_with":
                query = "{} WHERE n.{} =~ '(?i){}.*'".format(query, filter_field, filter_value)
        query = "{} RETURN {}".format(query, return_fields)
        fields = fields + ["_id"]
        return do_query(query, output_format=format, fields=fields)

    def api_all(self):
        query = "match (n:{}) return n".format(self.name)
        nodes = self.graph.cypher.execute(query)
        results = [x['n'].properties for x in nodes]
        return results

    def all(self, fields=None, limit=None, format="dict", order_by=None, desc=False):
        '''all returns all concepts, or up to a limit
        :param fields: select a subset of fields to return, default None returns all fields
        :param limit: return N=limit concepts only (default None)
        :param format: return format, either "df" "list" or dict (default)
        :param order_by: order the results by a particular field
        :param desc: if order by is not None, do descending (default True)
        '''
        if fields is None:
            fields = self.fields

        return_fields = ",".join(["n.{}".format(x) for x in fields] + ["ID(n)"])
        query = "MATCH (n:{}) RETURN {}".format(self.name, return_fields)

        if order_by != None:
            query = "{} ORDER BY n.{}".format(query, order_by)
            if desc is True:
                query = "{} desc".format(query)

        if limit != None:
            query = "{} LIMIT {}".format(query, limit)

        fields = fields + ["_id"]
        return do_query(query, fields=fields, output_format=format)

    def get(self, uid, field="id", get_relations=True, relations=None, label=None):
        ''' get returns one or more nodes based on a field of interest. If
            get_relations is true, will also return the default relations for
            the node, or those defined in the relations variable
        :param params: list of parameters to search for, eg [trm_123]
        :param field: field to search (default id)
        :param get_relations: default True, return relationships
        :paiam relations: list of relations to include. If not defined, will return all
        '''
        if label is None:
            label = self.name
        parents = self.graph.find(label, field, uid)
        nodes = []
        for parent in parents:
            new_node = {}
            new_node.update(parent.properties)
            new_node["_id"] = parent._id

            if get_relations is True:
                relation_nodes = dict()
                new_relations = self.graph.match(parent)
                for new_relation in new_relations:
                    new_relation_node = {}
                    new_relation_node.update(new_relation.end_node.properties)
                    new_relation_node["_id"] = new_relation.end_node._id
                    new_relation_node["_relation_id"] = new_relation._id
                    new_relation_node["relationship_type"] = new_relation.type
                    if new_relation.type in relation_nodes:
                        relation_nodes[new_relation.type].append(new_relation_node)
                    else:
                        relation_nodes[new_relation.type] = [new_relation_node]

                # Does the user want a filtered set?
                if relations != None:
                    relation_nodes = {k:v for k, v in relation_nodes.items() if k in relations}
                new_node["relations"] = relation_nodes

            nodes.append(new_node)

        return nodes


    def search_all_fields(self, params):
        if isinstance(params, str):
            params = [params]
        return_fields = ",".join(["c.{}".format(x) for x in self.fields] + ["ID(c)"])
        query = "MATCH (c:%s) WHERE c.{0} =~ '(?i).*{1}.*$' RETURN %s;" %(self.name, return_fields)

        # Combine queries into transaction
        tx = self.graph.cypher.begin()

        for field in self.fields:
            for param in params:
                tx.append(query.format(field, param))

        # Return as pandas data frame
        results = tx.commit()
        if not results or sum(len(res) for res in results) == 0:
            return {}

        df = pandas.DataFrame(columns=self.fields + ["_id"])
        i = 0
        for result in results:
            for record in result.records:
                attr_values = []
                for field in self.fields + ["ID(c)"]:
                    attr_name = "c.{}".format(field)
                    attr_values.append(getattr(record, attr_name, ""))
                df.loc[i] = attr_values
                i += 1
        return df.to_dict(orient="records")

    def get_relation(self, id, relation, label=None):
        ''' get nodes that are related to a given task
            :param task_id: id of node to look for relations from
            :relation: neo style relationship label ex. "ASSERTS"
            :fields: fields to retrieve from nodes related to task_id'''
        if label:
            label_substr = ':{}'.format(label)
        else:
            label_substr = ''
        query = '''MATCH (p:{})-[:{}]->(r{})
                   WHERE p.id = '{}'
                   RETURN r'''.format(self.name, relation, label_substr, id)
        relations = do_query(query, "null", "list")
        relations = [x[0].properties for x in relations]
        for rel in relations:
            rel['relationship'] = relation
        return relations

    def get_reverse_relation(self, id, relation, label=None):
        '''As opposed to get_relation this gets relations where the
           given id is the subject in the relationship, not the predicate.
           :param task_id: id of node to look for relations from
           :relation: neo style relationship label ex. "ASSERTS"
           :fields: fields to retrieve from nodes related to task_id'''
        if label:
            label_substr = ':{}'.format(label)
        else:
            label_substr = ''
        query = '''MATCH (p{})-[:{}]->(s:{})
                   WHERE s.id = '{}'
                   RETURN p'''.format(label_substr, relation, self.name, id)
        relations = do_query(query, "null", "list")
        relations = [x[0].properties for x in relations]
        for rel in relations:
            rel['relationship'] = relation
        return relations


    def get_full(self, value, field):
        ret = {'type': self.name}
        node = self.graph.find_one(self.name, field, value)
        if not node:
            return None
        ret = {**node.properties, **ret}
        node_id = node.properties['id']

        for rel in self.relations:
            ret[self.relations[rel]] = self.get_relation(node_id, rel)

        return ret


# Each type of Cognitive Atlas Class extends Node class

class Concept(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "concept"
        self.fields = ["id", "name", "definition_text", "alias"]
        self.relations = {
            "PARTOF": "concepts",
            "KINDOF": "concepts",
            "MEASUREDBY": "contrasts",
            "HASCITATION": "citations",
            "CLASSIFIEDUNDER": "conceptclasses",
        }
        self.color = "#3C7263" # sea green

    def get_full(self, value, field):
        ret = super().get_full(value, field)
        if not ret:
            return None
        # relationships is an old cogat api field for kindof and partofs
        child_rel = []
        child_rel.extend(self.get_reverse_relation(ret['id'], 'PARTOF'))
        child_rel.extend(self.get_reverse_relation(ret['id'], 'KINDOF'))
        for child in child_rel:
            child['direction'] = "child"
        parent_rel = []
        parent_rel.extend(self.get_relation(ret['id'], 'PARTOF'))
        parent_rel.extend(self.get_relation(ret['id'], 'KINDOF'))
        for parent in parent_rel:
            parent['direction'] = "parent"
        child_rel.extend(parent_rel)
        ret['relationships'] = child_rel
        return ret

class Task(Node):

    def __init__(self):
        super().__init__()
        self.name = "task"
        self.fields = ["id", "name", "definition_text"]
        self.relations = {
            "HASCONDITION": "conditions",
            "ASSERTS": "concepts",
            "HASINDICATOR": "indicators",
            "HASEXTERNALDATASET": "external_datasets",
            "HASIMPLEMENTATION": "implementations",
            "HASCITATION": "citation",
            "HASCONTRAST": "contrasts",
            "INBATTERY": "batteries"
        }
        self.color = "#63506D" #purple

    def get_full(self, value, field):
        ret = super().get_full(value, field)
        if not ret:
            return None
        value = ret['id']
        ret['contrasts'] = self.api_get_contrasts(value)
        ret['disorders'] = self.api_get_disorders(value)
        ret['concepts'] = self.api_update_concepts(ret['concepts'], value)
        return ret


    def api_update_concepts(self, concepts, task_id):
        for concept in concepts:
            concept['concept_id'] = concept.pop('id')
            query = ("MATCH (con:contrast)<-[:HASCONTRAST]-(t:task)-[:ASSERTS]->"
                     "(c:concept)-[:MEASUREDBY]->(con:contrast) "
                     "WHERE c.id = '{}' AND t.id = '{}' "
                     "RETURN con").format(concept['concept_id'], task_id)
            contrast = do_query(query, "null", "list")
            if contrast:
                concept['contrasts'] = [(x[0].properties['id'], x[0].properties['name'])
                                        for x in contrast]
        return concepts

    def api_get_contrasts(self, task_id):
        query = '''MATCH (t:task)-[:HASCONTRAST]->(c:contrast) WHERE t.id='{}'
                   RETURN c'''.format(task_id)
        contrasts = do_query(query, "null", "list")
        ret = [dict(x[0].properties) for x in contrasts]
        for contrast in ret:
            query = '''MATCH (cont:contrast)<-[r:HASCONTRAST]-(cond:condition)
                       WHERE cont.id='{}' return cont, r, cond'''.format(contrast['id'])
            results = settings.graph.cypher.execute(query)
            contrast.update({
                'conditions': [(x['cond'].properties, x['r'].properties) for x in results]
            })
        return ret


    def api_get_disorders(self, task_id):
        query = '''
            MATCH (t:task)-[:HASCONTRAST]->(c:contrast)-[dif:HASDIFFERENCE]->(d:disorder)
            WHERE t.id='{}' RETURN dif, d'''.format(task_id)
        disorders = do_query(query, ["null", "null2"], "list")
        ret_disorders = []
        for disorder in disorders:
            node = disorder[0]
            rel = disorder[1]
            # ret_disorders.append({**node.properties, 'id_disorder': node.properties.id})
            ret_disorders.append({
                'id': rel.properties['id'],
                'name': rel.properties['name'],
                'id_user': node.properties['id_user'],
                'id_disorder': node['properties.id'],
                'id_task': task_id,
                'id_contrast': rel.properties['id_contrast'],
                'event_stamp': rel.properties['event_stamp']
            })
        return ret_disorders

    # the relationship itself contains data that should be presented in api
    # no functions right now for getting end node and relation properties
    def api_get_indicators(self, task_id):
        query = '''MATCH (t:task)-[rel:HASINDICATOR]->(i:indicator)
                   WHERE t.id = '{}' return rel, c)'''


    def get_contrasts(self, task_id):
        '''get_contrasts looks up the contrasts(s) associated with a task, along with concepts
        :param task_id: the task unique id (trm|tsk_*) for the task'''

        fields = ["contrast.id", "contrast.creation_time", "contrast.name",
                  "contrast.last_updated", "ID(contrast)"]

        return_fields = ",".join(fields)
        query = '''MATCH (t:task)-[:HASCONDITION]->(c:condition)
                   WHERE t.id='{}'
                   WITH c as condition
                   MATCH (condition)-[:HASCONTRAST]->(con:contrast)
                   WITH con as contrast
                   RETURN {}'''.format(task_id, return_fields)

        fields = [x.replace(".", "_") for x in fields]
        fields[-1] = "_id" # consistent name for graph node id

        result = do_query(query, fields=fields, drop_duplicates=False, output_format="df")
        contrast_name = [r[0] if isinstance(r, list) else r for r in result['contrast_name']]
        result["contrast_name"] = contrast_name
        result = result.drop_duplicates()
        return result.to_dict(orient="records")


    def get_conditions(self, task_id):
        '''get_conditions looks up the condition(s) associated with a task
        :param task_id: the task unique id (trm|tsk_*) for the task
        '''
        fields = ["condition.id", "condition.name", "condition.last_updated",
                  "condition.creation_time", "ID(condition)"]

        return_fields = ",".join(fields)
        query = '''MATCH (t:task)-[:HASCONDITION]->(c:condition)
                   WHERE t.id='{}'
                   WITH c as condition
                   RETURN {}'''.format(task_id, return_fields)
        fields = [x.replace(".", "_") for x in fields]
        fields[-1] = "_id"

        return do_query(query, fields=fields)

class Disorder(Node):

    def __init__(self):
        super().__init__()
        self.name = "disorder"
        self.fields = ["id", "name", "classification", "definition",
                       "event_stamp", "id_user", "is_a", "id_protocol",
                       "is_a_fulltext", "is_a_protocol"]
        self.color = "#337AB7" # neurovault blue
        self.relations = {
            "ISA": "disorders",
            "HASCITATION": "citations",
            "HASLINK": "external_links"
        }

class Trait(Node):

    def __init__(self):
        super().__init__()
        self.name = "trait"
        self.fields = ["id", "name", "definition",
                       "event_stamp", "id_user"]
        self.color = "#337AB7" # neurovault blue
        self.relations = {
            "HASCITATION": "citations",
            "HASLINK": "external_links",
            "MEASUREDBY": "contrasts"
        }

class Behavior(Node):

    def __init__(self):
        super().__init__()
        self.name = "behavior"
        self.fields = ["id", "name", "definition",
                       "event_stamp", "id_user"]
        self.color = "#337AB7" # neurovault blue
        self.relations = {
            "HASCITATION": "citations",
            "HASLINK": "external_links",
            "MEASUREDBY": "contrasts"
        }


class Condition(Node):

    def __init__(self):
        super().__init__()
        self.name = "condition"
        self.fields = ["id", "name", "description"]
        self.color = "#BC1079" # dark pink
        self.relations = {"HASCONTRAST": "contrasts"}

class Contrast(Node):
    def __init__(self):
        super().__init__()
        self.name = "contrast"
        self.fields = ["id", "name", "description"]
        self.color = "#D89013" #gold
        self.relations = {"HASDIFFERENCE": "disorders"}

    def get_conditions(self, contrast_id, fields=None):
        '''get_conditions returns conditions associated with a contrast
        :param contrast_id: the contrast unique id (cnt) for the task
        :param fields: condition fields to return
        '''

        if fields is None:
            fields = ["condition.creation_time", "condition.id",
                      "condition.last_updated", "condition.name", "ID(condition)"]

        return_fields = ",".join(fields)
        query = '''MATCH (cond:condition)-[:HASCONTRAST]->(c:contrast)
                   WHERE c.id='{}'
                   WITH cond as condition
                   RETURN {}'''.format(contrast_id, return_fields)

        fields = [x.replace(".", "_") for x in fields]
        fields[-1] = "_id"

        return do_query(query, fields=fields)


    def get_concepts(self, contrast_id, fields=None):
        '''get_concepts returns conditions associated with a contrast
        :param contrast_id: the contrast unique id (cnt) for the task
        :param fields: condition fields to return
        '''

        if fields is None:
            fields = ["concept.creation_time", "concept.id", "concept.description",
                      "concept.last_updated", "concept.name", "ID(concept)"]

        return_fields = ",".join(fields)
        query = '''MATCH (con:concept)-[:MEASUREDBY]->(c:contrast)
                   WHERE c.id='{}'
                   WITH con as concept
                   RETURN {}'''.format(contrast_id, return_fields)

        fields = [x.replace(".", "_") for x in fields]
        fields[-1] = "_id"
        return do_query(query, fields=fields)

    def api_get_concepts(self, contrast_id):
        concepts = self.get_reverse_relation(contrast_id, "MEASUREDBY")
        concept_ids = [x['id'] for x in concepts]
        concept = Concept()
        concepts = [concept.get_full(x, 'id') for x in concept_ids]
        return concepts

    def get_tasks(self, contrast_id, fields=None):
        '''get_task looks up the task(s) associated with a contrast
        :param contrast_id: the contrast unique id (cnt) for the task
        :param fields: task fields to return
        '''
        if fields is None:
            fields = ["task.creation_time", "task.definition", "task.id", "task.last_updated",
                      "task.name", "ID(task)"]

        # task --> [hascondition] --> condition
        # condition -> [hascontrast] -> contrast

        return_fields = ",".join(fields)
        query = '''MATCH (c:concept)-[:MEASUREDBY]->(co:contrast)
                   WHERE co.id='{}' WITH co as contrast
                   MATCH (c:condition)-[:HASCONTRAST]->(contrast) WITH c as condition
                   MATCH (t:task)-[:HASCONDITION]->(condition)
                   WITH DISTINCT t as task
                   RETURN {}'''.format(contrast_id, return_fields)

        fields = [x.replace(".", "_") for x in fields]
        fields[-1] = "_id"
        return do_query(query, fields=fields)


class Battery(Node):

    def __init__(self):
        super().__init__()
        self.name = "battery"
        self.fields = ["id", "name", "collection", "collection_description"]
        self.color = "#4BBE00" # bright green
        self.relations = {
            "HASCITATION": "citations",
            "HASINDICATOR": "indicators",
            "INBATTERY": "constituents"
        }

class Theory(Node):

    def __init__(self):
        super().__init__()
        self.name = "theory"
        self.fields = ["id", "name", "collection_description"]
        self.color = "#BE0000" # dark red
        self.relations = {"HASCITATION": "citations"}

class Implementation(Node):

    def __init__(self):
        super().__init__()
        self.name = "implementation"
        self.fields = ["implementation_uri", "implementation_name", "implementation_description"]

class ExternalDataset(Node):

    def __init__(self):
        super().__init__()
        self.name = "external_dataset"
        self.fields = ["dataset_name", "dataset_uri"]

class Indicator(Node):

    def __init__(self):
        super().__init__()
        self.name = "indicator"
        self.fields = ["type"]

class Citation(Node):

    def __init__(self):
        super().__init__()
        self.name = "citation"
        self.fields = ["citation_url", "citation_comment", "citation_desc",
                       "citation_authors", "citation_type", "citation_pubname",
                       "citation_pubdate", "citation_pmid", "citation_source",
                       "id", "name"]

class Assertion(Node):

    def __init__(self):
        super().__init__()
        self.name = "assertion"
        self.fields = ["id", "name", "event_stamp", "truth_value",
                       "id_subject_def", "user_id", "flag_for_curator",
                       "confidence_level"]
        self.relations = {
            "PREDICATE": "tasks",
            "SUBJECT": "concepts",
            "PREDICATE_DEF": "contrasts",
            "INTHEORY": "theories",
            "HASCITATION": "citations"
        }

class User(Node):

    def __init__(self):
        super().__init__()
        self.name = "user"
        self.fields = ["id", "username"]
        self.relations = {
            "CREATED": "nodes"
        }

class ExternalLink(Node):

    def __init__(self):
        super().__init__()
        self.name = "external_link"
        self.fields = ["uri"]

class ConceptClass(Node):

    def __init__(self):
        super().__init__()
        self.name = "concept_class"
        self.fields = ["id", "name", "description", "display_order"]

class Disambiguation(Node):
    def __init__(self):
        super().__init__()
        self.name = "disambiguation"
        self.fields = ["id", "name", "description"]
        self.relations = {
            "DISAMBIGUATES": "concepts",
            "DISAMBIGUATES": "tasks",
            "DISAMBIGUATES": "behavior",
            "DISAMBIGUATES": "traits",
        }

# General search function across nodes
def search(searchstring, fields=["name", "id"], node_type=None):
    if isinstance(fields, str):
        fields = [fields]
    return_fields = ",".join(["n.{}".format(x) for x in fields] + ["ID(n)"])

    # Customize if specific kind of node requested
    if node_type is None:
        node_type = ""
    else:
        node_type = ":{}".format(node_type.lower())
    
    searchstring = re.escape(searchstring)

    query = '''MATCH (n%s)
               WHERE str(n.name) =~ '(?i).*%s.*'
               RETURN %s, labels(n);''' %(node_type, searchstring.__repr__()[1:-1], return_fields)
    fields = fields + ["_id", "label"]
    result = do_query(query, fields=fields, drop_duplicates=False, output_format="df")
    result["label"] = [r[0] for r in result['label']]
    result = result.drop_duplicates()
    return result.to_dict(orient="records")

def search_contrast(searchstring):
    searchstring = re.escape(searchstring)

    query = '''match (t:task)-[:HASCONTRAST]->(c:contrast) 
               where str(c.name) =~ '(?i).*{0}.*' or str(t.name) =~ '(?i).*{0}.*'
               return t.id, t.name, c.id, c.name
            '''.format(searchstring.__repr__()[1:-1])

    result = do_query(query, fields=['tid', 'tname', 'cid', 'cname'], drop_duplicates=True, output_format="df")
    return result.to_dict(orient="records")


# General get function across nodes, get by id
def get(nodeid, fields=["name", "id"]):
    if isinstance(fields, str):
        fields = [fields]
    return_fields = ",".join(["n.%s" %x for x in fields] + ["ID(n)"])
    query = '''MATCH (n) WHERE str(n.name) =~ '(?i).*%s.*' RETURN %s;''' %(nodeid, return_fields)
    fields = fields + ["_id"]
    return do_query(query, fields=fields)


# Functions to generate cypher queries for nodes and relations
def cypher_node(uid, node_type, name, count):
    '''cyper_node creates a cypher node for including in a gist
    :param uid: the unique id of the node
    :param node_type: the type of node (eg, concept)
    :param name: the name of the node
    :param count: the node id (count) used to define relations and reference the node
    '''
    return 'create (_%s:`%s` {`id`:"%s", `name`:"%s"})' %(count, node_type, uid, name)

def cypher_relation(relation_name, count1, count2):
    '''cyper_relation creates a cypher relation for including in a gist
    :param relation_name: the name of the relation
    :param count1: the name of the node
    :param count2: the node id (count) used to define relations and reference the node
    '''
    return 'create _%s-[:`%s`]->_%s' %(count1, relation_name, count2)
