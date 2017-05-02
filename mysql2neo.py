from py2neo import Graph, Node, Relationship
import pymysql

conn = pymysql.connect(host='localhost', user='root', db='cogat')
cursor = conn.cursor()

graph = Graph("http://192.168.99.100:7474/db/data/")

# import tasks
sql = "select id, id_user, term_alias, event_stamp from table_term where term_type='task'"
cursor.execute(sql)
tasks = cursor.fetchall()

print("filling in additional task/concept details...")
for task in tasks:
    gtask = graph.find_one("task", property_key="id", property_value=task[0])
    if not gtask:
        raise Exception(task)
    gtask.properties['id_user'] = task[1]
    gtask.properties['alias'] = task[2]
    gtask.properties['event_stamp'] = task[3]
    gtask.push()

print("filling in additional definition details...")
sql = "select * from table_definition"
cursor.execute(sql)
definitions = cursor.fetchall()
for definition in definitions:
    gtask = graph.find_one("task", property_key="id", property_value=definition[2])
    if not gtask:
        gtask = graph.find_one("concept", property_key="id", property_value=definition[2])
    if not gtask:
        print(definition)
        continue
    gtask.properties['def_id'] = definition[0]
    gtask.properties['def_id_user'] = definition[1]
    gtask.properties['def_event_stamp'] = definition[4]
    gtask.properties['id_concept_class'] = definition[5]
    gtask.push()
    

# import indicators
print("indicators...")
sql = "select distinct indicator_text from type_indicator"
cursor.execute(sql)
indicators = cursor.fetchall()

for indicator in indicators:
    if graph.find_one("indicator", property_key="type", property_value=indicator[0]):
        continue
    gret = graph.create(Node("indicator", type=indicator[0]))
    print(gret)
    

print("indicator relationships...")
sql = "select * from type_indicator"
cursor.execute(sql)
indicators = cursor.fetchall()

for indicator in indicators:
    start_node = graph.find_one("task", property_key="id",
                                property_value=indicator[2])
    end_node = graph.find_one("indicator", property_key="type",
                              property_value=indicator[3])

    match = graph.match_one(start_node=start_node, rel_type="HASINDICATOR",
                            end_node=end_node)
    if start_node and end_node and not match:
        gret = graph.create(Relationship(start_node, "HASINDICATOR", end_node,
                                         id=indicator[0], id_user=indicator[1],
                                         event_stamp=indicator[4]))
        print(gret)

# import external datasets
print("external datasets...")
sql = "select * from external_datasets"
cursor.execute(sql)
external_datasets = cursor.fetchall()

for external_dataset in external_datasets:
    found = graph.find_one("external_dataset", property_key="id",
                           property_value=external_dataset[0])
    if not found:
        gret = graph.create(
            Node("external_dataset", id=external_dataset[0],
                 id_term=external_dataset[1], dataset_name=external_dataset[2],
                 dataset_uri=external_dataset[3], id_user=external_dataset[4],
                 event_stamp=external_dataset[5])
        )
        print(gret)

    start_node = graph.find_one("task", property_key="id",
                                property_value=external_dataset[1])
    end_node = graph.find_one("external_dataset", property_key="id",
                              property_value=external_dataset[0])

    match = graph.match_one(start_node=start_node, rel_type="HASEXTERNALDATASET",
                            end_node=end_node)
    if start_node and end_node and not match:
        gret = graph.create(Relationship(start_node, "HASEXTERNALDATASET",
                                          end_node))
        print(gret)

# import implementations
print("implementations...")
sql = "select * from table_implementation"
cursor.execute(sql)
implementations = cursor.fetchall()

for implementation in implementations:
    found = graph.find_one("implementation", property_key="id", property_value=implementation[0])
    if not found:
        gret = graph.create(Node("implementation", id=implementation[0],
                                 id_task=implementation[1],
                                 implementation_name=implementation[2],
                                 implementation_uri=implementation[3],
                                 id_user=implementation[4],
                                 event_stamp=implementation[5],
                                 implementation_description=implementation[5]))
        print(gret)

    start_node = graph.find_one("task", property_key="id",
                                property_value=implementation[1])
    end_node = graph.find_one("implementation", property_key="id",
                              property_value=implementation[0])

    match = graph.match_one(start_node=start_node, rel_type="HASIMPLEMENTATION",
                            end_node=end_node)

    if start_node and end_node and not match:
        gret = graph.create(Relationship(start_node, "HASIMPLEMENTATION",
                            end_node))
        print(gret)

# import citations
print("citations...")
sql = "select * from table_citation"
cursor.execute(sql)
citations = cursor.fetchall()

for citation in citations:
    found = graph.find_one("citation", property_key="id",
                           property_value=citation[0])
    if not found:
        gret = graph.create(
            Node("citation", id=citation[0], id_user=citation[1],
                 citation_type=citation[2], citation_desc=citation[3],
                 citation_url=citation[4], citation_source=citation[5],
                 citation_pubdate=citation[6], citation_authors=citation[7],
                 citation_pubname=citation[8], citation_comment=citation[9],
                 citation_pmid=citation[10], event_stamp=citation[11])
        )
        print(gret)

sql = "select * from match_citation_entity"
cursor.execute(sql)
cit_rels = cursor.fetchall()

for cit_rel in cit_rels:
    query = "match (n) where n.id = '{}' return n".format(cit_rel[2])
    nodes = graph.cypher.execute(query)
    if len(nodes) < 1:
        continue
    start_node = nodes[0]['n']
    end_node = graph.find_one("citation", property_key='id', property_value=cit_rel[1])

    match = graph.match_one(start_node=start_node, rel_type="HASCITATION", end_node=end_node)
    if start_node and end_node and not match:
        gret = graph.create(Relationship(start_node, "HASCITATION", end_node))
        print(gret)

# import disorders
print("disorders...")
sql = "select * from disorder_import"
cursor.execute(sql)
disorders = cursor.fetchall()

for disorder in disorders:
    found = graph.find_one("disorder", property_key="id",
                           property_value=disorder[2])

    if not found:
        gret = graph.create(
            Node("disorder", id=disorder[2], id_protocol=disorder[3],
                 name=disorder[4], definition=disorder[5], is_a=disorder[6],
                 is_a_protocol=disorder[7], is_a_fulltext=disorder[8],
                 id_user=disorder[9], event_stamp=disorder[10])
        )
        print(gret)

sql = "select * from match_disorder_assertions"
cursor.execute(sql)
dis_asserts = cursor.fetchall()

for dis_assert in dis_asserts:
    end_node = graph.find_one("disorder", property_key='id', property_value=dis_assert[2])
    start_node = graph.find_one("contrast", property_key='id', property_value=dis_assert[4])
    match = graph.match_one(start_node=start_node, rel_type="HASDIFFERENCE", end_node=end_node)
    if start_node and end_node and not match:
        gret = graph.create(Relationship(start_node, "HASDIFFERENCE", end_node,
                            id_task=[dis_assert[3]], id=dis_assert[0], event_stamp=dis_assert[5]))
        print(gret)


# import concept class
print("concept class types...")
sql = "select * from type_concept"
cursor.execute(sql)
types = cursor.fetchall()
for type in types:
    pass
    #found = graph.find_one("concept_class", property_key="id",
