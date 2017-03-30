from py2neo import Graph

from django.test import TestCase

from cognitive.apps.atlas.query import Node, Task
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
        self.node1 = self.node.create(name=self.node_name, properties=self.node_properties)
        self.assertEqual(self.node1.properties['name'], self.node_name)
        self.assertEqual(self.node1.properties['test_key'], self.node_properties['test_key'])

    def test_count_delete(self):
        count = self.node.count()
        self.node1 = self.node.create(name=self.node_name, properties=self.node_properties)
        self.assertEqual(count + 1, self.node.count())

    def test_link(self):
        self.node1 = self.node.create(name=self.node_name, properties=self.node_properties)
        self.node2 = self.node.create(name=self.node_name, properties=self.node_properties)
        relation = self.node.link(self.node1.properties['id'], self.node2.properties['id'], "GENERIC")
        self.assertEqual(relation.start_node.properties['id'], self.node1.properties['id'])
        self.assertEqual(relation.end_node.properties['id'], self.node2.properties['id'])

    def test_cypher(self):
        pass

    def test_get_graph(self):
        pass

    def test_all(self):
        pass
    
    def test_serach_all_fields(self):
        pass

class TaskTest(TestCase):
    def get_contrasts(self):
        pass

    def get_conditions(self):
        pass

class ContrastTest(TestCase):
    def test_get_conditions(self):
        pass

    def test_get_concepts(self):
        pass

    def test_get_tasks(self):
        pass

class GraphUtilsTest(TestCase):
    def test_search(self):
        pass

    def test_get(self):
        pass

    def test_cypher_node(self):
        pass

    def test_cypher_relation(self):
        pass
