from py2neo import Graph

from django.test import TestCase

from cognitive.apps.atlas.query import (
    Node, Task, Condition, Concept, Contrast, search, get, cypher_node,
    cypher_relation
)
from cognitive.settings import graph


class NodeTest(TestCase):
    def setUp(self):
        self.node = Node()
        self.node1 = None
        self.node2 = None
        self.node_name = "test_name"
        self.node_properties = {'test_key': 'test_value'}
        self.graph = Graph("http://graphdb:7474/db/data/")

    def tearDown(self):
        if self.node1:
            self.node1.delete_related()
            self.node1.delete()
        if self.node2:
            self.node2.delete_related()
            self.node2.delete()

    def test_create(self):
        self.node1 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        self.assertEqual(self.node1.properties['name'], self.node_name)
        self.assertEqual(
            self.node1.properties['test_key'],
            self.node_properties['test_key'])

    def test_count_delete(self):
        count = self.node.count()
        self.node1 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        self.assertEqual(count + 1, self.node.count())

    def test_link(self):
        self.node1 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        self.node2 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        relation = self.node.link(
            self.node1.properties['id'],
            self.node2.properties['id'],
            "GENERIC")
        self.assertEqual(
            relation.start_node.properties['id'],
            self.node1.properties['id'])
        self.assertEqual(
            relation.end_node.properties['id'],
            self.node2.properties['id'])

    def test_cypher(self):
        self.node1 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        self.node2 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        relation = self.node.link(
            self.node1.properties['id'],
            self.node2.properties['id'],
            "GENERIC")
        result = self.node.cypher(self.node1.properties['id'])
        self.assertIn("generic", result['nodes'][0])
        self.assertIn(str(self.node1._id), result['nodes'][0])

    def test_get_graph(self):
        self.node1 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        self.node2 = self.node.create(
            name=self.node_name,
            properties=self.node_properties)
        relation = self.node.link(
            self.node1.properties['id'],
            self.node2.properties['id'],
            "GENERIC")
        result = self.node.get_graph(self.node1.properties['id'])
        self.assertEqual(
            result['nodes'][0]['name'],
            self.node1.properties['name'])
        self.assertEqual(
            result['nodes'][1]['name'],
            self.node2.properties['name'])
        self.assertEqual("GENERIC", result['links'][0]['type'])

    def test_all(self):
        pass

    def test_serach_all_fields(self):
        pass


class NodeChildrenTest(TestCase):
    def setUp(self):
        self.task = Task()
        self.node_name = "test_name"
        self.node_properties = {'test_key': 'test_value'}
        self.graph = Graph("http://graphdb:7474/db/data/")
        self.task1 = self.task.create(
            name=self.node_name,
            properties=self.node_properties)
        self.task2 = self.task.create(
            name=self.node_name,
            properties=self.node_properties)
        condition = Condition()
        self.cond = condition.create(
            name=self.node_name,
            properties=self.node_properties)
        contrast = Contrast()
        self.cont = contrast.create(
            name=self.node_name,
            properties=self.node_properties)
        concept = Concept()
        self.con = concept.create(
            name=self.node_name,
            properties=self.node_properties)
        self.task.link(
            self.task1.properties['id'],
            self.cond.properties['id'],
            "HASCONDITION",
            endnode_type='condition')
        self.task.link(
            self.task1.properties['id'],
            self.con.properties['id'],
            "ASSERTS",
            endnode_type='concept')
        condition.link(
            self.cond.properties['id'],
            self.cont.properties['id'],
            "HASCONTRAST",
            endnode_type='contrast')
        concept.link(
            self.con.properties['id'],
            self.cont.properties['id'],
            "MEASUREDBY",
            endnode_type='contrast')

    def tearDown(self):
        self.task1.delete_related()
        self.task2.delete_related()
        self.cond.delete_related()
        self.cont.delete_related()
        self.con.delete_related()
        self.task1.delete()
        self.task2.delete()
        self.cond.delete()
        self.cont.delete()
        self.con.delete()

    def test_task_get_contrasts(self):
        contrasts = self.task.get_contrasts(self.task1.properties['id'])
        self.assertEqual(len(contrasts), 1)
        self.assertEqual(
            contrasts[0]['contrast_id'],
            self.cont.properties['id'])

    def test_task_get_conditions(self):
        conditions = self.task.get_conditions(self.task1.properties['id'])
        self.assertEqual(len(conditions), 1)
        self.assertEqual(
            conditions[0]['condition_id'],
            self.cond.properties['id'])

    def test_contrast_get_conditions(self):
        contrast = Contrast()
        conditions = contrast.get_conditions(self.cont.properties['id'])
        self.assertEqual(len(conditions), 1)
        self.assertEqual(
            conditions[0]['condition_id'],
            self.cond.properties['id'])

    def test_contrast_get_concepts(self):
        contrast = Contrast()
        concepts = contrast.get_concepts(self.cont.properties['id'])
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0]['concept_id'], self.con.properties['id'])

    def test_contrast_get_tasks(self):
        contrast = Contrast()
        tasks = contrast.get_tasks(self.cont.properties['id'])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['task_id'], self.task1.properties['id'])


class GraphUtilsTest(TestCase):
    def setUp(self):
        self.task = Task()
        self.node_name = "test_name"
        self.node_properties = {'test_key': 'test_value'}
        self.graph = Graph("http://graphdb:7474/db/data/")
        self.task1 = self.task.create(
            name=self.node_name,
            properties=self.node_properties)
        self.task2 = self.task.create(
            name=self.node_name,
            properties=self.node_properties)
        condition = Condition()
        self.cond = condition.create(
            name=self.node_name,
            properties=self.node_properties)
        contrast = Contrast()
        self.cont = contrast.create(
            name=self.node_name,
            properties=self.node_properties)
        concept = Concept()
        self.con = concept.create(
            name=self.node_name,
            properties=self.node_properties)
        self.task.link(
            self.task1.properties['id'],
            self.cond.properties['id'],
            "HASCONDITION",
            endnode_type='condition')
        self.task.link(
            self.task1.properties['id'],
            self.con.properties['id'],
            "ASSERTS",
            endnode_type='concept')
        condition.link(
            self.cond.properties['id'],
            self.cont.properties['id'],
            "HASCONTRAST",
            endnode_type='contrast')
        concept.link(
            self.con.properties['id'],
            self.cont.properties['id'],
            "MEASUREDBY",
            endnode_type='contrast')

    def tearDown(self):
        self.task1.delete_related()
        self.task2.delete_related()
        self.cond.delete_related()
        self.cont.delete_related()
        self.con.delete_related()
        self.task1.delete()
        self.task2.delete()
        self.cond.delete()
        self.cont.delete()
        self.con.delete()

    def test_search(self):
        # we create 5 nodes all with the same name, this should find them all
        result = search('test_name')
        self.assertEqual(len(result), 5)

    '''
    def test_get(self):
        result = get(self.task1.properties['name'])
        self.assertEqual(len(result), 1)
    '''

    ''' ignoring gist functions for now
    def test_cypher_node(self):
        pass

    def test_cypher_relation(self):
        pass
    '''
