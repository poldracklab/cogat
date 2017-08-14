import html
import re

from py2neo import Graph, Node, Relationship
import pymysql

conn = pymysql.connect(host='localhost', user='root', db='cogat')
cursor = conn.cursor()

graph = Graph("http://graphdb:7474/db/data/")

def make_node(nodetype, uid, name, properties=None, property_key="id"):
    node = None
    if graph.find_one(nodetype, property_key=property_key, property_value=uid) is None:
        info = "Creating {}:{}, {}".format(nodetype, name, uid)
        print(info.encode('utf-8'))
        timestamp = graph.cypher.execute("RETURN timestamp()").one
        node = Node(
            str(nodetype),
            name=html.unescape(str(name)),
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

def make_relation(startnode, rel_type, endnode, properties=None):
    relation = None
    if graph.match_one(
            start_node=startnode,
            rel_type=rel_type,
            end_node=endnode) is None:
        relation = Relationship(startnode, rel_type, endnode)
        print(
            "Creating relation {} [{}] {}".format(
                startnode.properties["name"],
                rel_type,
                endnode.properties["name"]
            ).encode('utf-8')
        )
        graph.create(relation)
        if properties is not None:
            for property_name in properties.keys():
                relation.properties[property_name] = properties[property_name]
            relation.push()
    return relation

def find_node(nodetype, property_value, property_key='id'):
    try:
        node = graph.find_one(
            nodetype,
            property_key=property_key,
            property_value=property_value)
    except BaseException:
        node = None
    return node

def get_def(uid):
    def_sql = "select definition_text from table_definition where id_term='{}'".format(uid)
    cursor.execute(def_sql)
    defs = cursor.fetchall()
    if len(defs) > 1:
        raise Exception("more than one task definition for term {}".format(uid))
    elif len(defs) == 1:
        return defs[0][0]
    else:
        return ""

def import_tasks():
    sql = "select id, term_text from table_term where term_type='task'"
    cursor.execute(sql)
    tasks = cursor.fetchall()
    for task in tasks:
        props = {}
        uid = task[0]
        name = task[1]
        props['definition_text'] = get_def(uid)
        make_node("task", uid, name, props)

def import_conditions():
    sql = "select id, id_user, id_term, condition_text, condition_description, event_stamp from type_condition"
    cursor.execute(sql)
    conditions = cursor.fetchall()
    for cond in conditions:
        props = {}
        props["condition_text"] = cond[3]
        props["id_user"] = cond[1]
        props["event_stamp"] = cond[5]
        props["condition_description"] = cond[4]
        task_id = cond[2]
        uid = cond[0]
        new_cond = make_node("condition", uid, cond[3], props)
        if new_cond is None:
            raise Exception("failed to make condition {}".format(cond[0]))

        task_node = find_node("task", task_id)
        if task_node:
            make_relation(task_node, "HASCONDITION", new_cond)

def import_concepts():
    sql = "select id, term_text from table_term where term_type='concept'"
    cursor.execute(sql)
    concepts = cursor.fetchall()
    for con in concepts:
        props = {}
        uid = con[0]
        name = con[1]
        props["definition_text"] = get_def(uid)
        make_node("concept", uid, name, props)

def import_contrasts():
    sql = "select id, id_user, id_term, contrast_text, event_stamp from type_contrast"
    cursor.execute(sql)
    contrasts = cursor.fetchall()
    for cont in contrasts:
        props = {}
        uid = cont[0]
        name = cont[3]
        task_id = cont[2]
        props["id_user"] = cont[1]
        props["event_stamp"] = cont[4]
        new_cont = make_node("contrast", uid, name, props)

        task_node = find_node("task", task_id)
        if task_node:
            make_relation(task_node, "HASCONTRAST", new_cont)

def import_assertions():
    sql = '''select id, id_user, id_subject, id_relation, id_predicate,
                    id_type, confidence_level, text_description,
                    event_stamp, id_subject_def, id_predicate_def,
                    truth_value, flag_for_curator
             from table_assertion'''
    cursor.execute(sql)
    assertions = cursor.fetchall()

    for assertion in assertions:
        props = {}
        props["id"] = assertion[0]
        props["user_id"] = assertion[1]
        props["confidence_level"] = assertion[6]
        props["text_description"] = assertion[7]
        props["event_stamp"] = assertion[8]
        sub_def = assertion[9]
        if sub_def is "NADA":
            sub_def = ""
        props["id_subject_def"] = sub_def
        props["truth_value"] = assertion[11]
        props["flag_for_curator"] = assertion[12]

        subject = assertion[2]
        id_rel = assertion[3]
        predicate = assertion[4]
        rel_type = assertion[5]
        id_predicate_def = assertion[10]

        assert_node = make_node("assertion", props.pop('id'),
                                props.pop('text_description'), props)

        if rel_type == "concept-task":
            tasknode = find_node("task", property_value=predicate)
            conceptnode = find_node("concept", property_value=subject)
            contrastnode = find_node("contrast", property_value=id_predicate_def)

            # Contrast is measured by contrast
            if contrastnode is not None and conceptnode is not None:
                relation = make_relation(
                    conceptnode, "MEASUREDBY", contrastnode)

            if tasknode and conceptnode:
                make_relation(tasknode, "ASSERTS", conceptnode)

            if tasknode and conceptnode and contrastnode:
                make_relation(assert_node, "PREDICATE", tasknode)
                make_relation(assert_node, "SUBJECT", conceptnode)
                make_relation(assert_node, "PREDICATE_DEF", contrastnode)

        elif rel_type == "concept-concept":
            conceptnode1 = find_node("concept", property_value=subject)
            conceptnode2 = find_node("concept", property_value=predicate)

            # Figure out relationship type
            if id_rel == 'T1':
                relationship_type = "KINDOF"
            elif id_rel == 'T2':
                relationship_type = "PARTOF"
            elif id_rel == 'T10':
                relation_type = "SYNONYM"
            elif id_rel == 'T5':
                relation_type = "PRECEDEDBY"
            else:
                print(('concept to concept relationship type not found in '
                       'description: {}'''.format(props['description'])))

            # Contrast is measured by contrast
            if conceptnode1 and conceptnode2:
                relation = make_relation(
                    conceptnode1, relationship_type, conceptnode2)
                make_relation(assert_node, "PREDICATE", conceptnode2)
                make_relation(assert_node, "SUBJECT", conceptnode1)

        elif rel_type == "task-task":
            tasknode1 = find_node("task", property_value=subject)
            tasknode2 = find_node("task", property_value=predicate)

            if id_rel == 'T10':
                relation_type = "SYNONYM"
            elif id_rel == 'T15':
                relation_type = "DERIVEDFROM"

            # Task is descended from task
            if tasknode1 and tasknode2:
                relation = make_relation(tasknode1, relationship_type, tasknode2)
                make_relation(assert_node, "PREDICATE", tasknode2)
                make_relation(assert_node, "SUBJECT", tasknode1)

def import_battery():
    sql = ("select id, collection_name, collection_alias, id_user, "
           "event_stamp, collection_description, collection_date_introduced, "
           "collection_publisher, flag_for_curator, website "
           "from table_task_collection")
    cursor.execute(sql)
    batteries = cursor.fetchall()
    for battery in batteries:
        props = {}
        props["collection_alias"] = battery[2]
        props["id_user"] = battery[3]
        props["event_stamp"] = battery[4]
        props["collection_description"] = battery[5]
        props["collection_date_introduced"] = battery[6]
        props["collection_publisher"] = battery[7]
        props["flag_for_curator"] = battery[8]
        props["website"] = battery[9]
        uid = battery[0]
        name = battery[1]

        make_node("battery", uid, name, props)

def import_battery_relations():
    sql = ("select id_user, id_term, id_collection, event_stamp from match_collection_tasks")
    cursor.execute(sql)
    batt_rels = cursor.fetchall()
    for batt_rel in batt_rels:
        props = {}
        props["id_user"] = batt_rel[0]
        props["event_stamp"] = batt_rel[3]
        task_id = batt_rel[1]
        uid = batt_rel[2]

        task = find_node("task", task_id)
        batt = find_node("battery", uid)
        if task and batt:
            make_relation(task, "INBATTERY", batt, props)

def import_theory():
    sql = ("select id, collection_name, collection_alias, concept_class, "
           "id_user, event_stamp, collection_description, flag_for_curator "
           "from table_theory_collection")
    cursor.execute(sql)
    theories = cursor.fetchall()
    for theory in theories:
        props = {}
        props["collection_alias"] = theory[2]
        props["id_user"] = theory[4]
        props["event_stamp"] = theory[5]
        props["collection_description"] = theory[6]
        props["flag_for_curator"] = theory[7]
        uid = theory[0]
        name = theory[1]
        make_node("theory", uid, name, props)

def import_theory_relations():
    sql = ("select id_user, id_assertion, id_collection, event_stamp from match_collection_assertions")
    cursor.execute(sql)
    theory_asserts = cursor.fetchall()

    for theory_assert in theory_asserts:
        props = {}
        props["event_stamp"] = theory_assert[3]
        props["id_user"] = theory_assert[0]
        theory = find_node("theory", theory_assert[2])
        assertion = find_node("assertion", theory_assert[1])

        if theory and assertion:
            make_relation(assertion, "INTHEORY", theory, props)

def import_collection_relations():
    sql = ("select id, id_user, id_included_collection, id_collection,"
           "event_stamp from match_collection_collections")
    cursor.execute(sql)
    coll_rels = cursor.fetchall()

    for coll_rel in coll_rels:
        props = {}
        props["id_user"] = coll_rel[1]
        props["event_stamp"] = coll_rel[4]

        coll1 = find_node("battery", coll_rel[2])
        coll2 = find_node("battery", coll_rel[3])

        if coll1 and coll2:
            # INBATTERY? PARTOF?
            make_relation(coll1, "PARTOF", coll2)

if __name__ == '__main__':
    graph = Graph("http://graphdb:7474/db/data/")
    graph.delete_all()
    import_tasks()
    import_conditions()
    import_concepts()
    import_contrasts()
    import_assertions()
    import_battery()
    import_battery_relations()
    import_theory()
    import_theory_relations()
    import_collection_relations()
