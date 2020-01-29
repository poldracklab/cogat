import json

from django.urls import reverse
from django.test import TestCase


from cognitive.apps.atlas.query import Concept, Disorder, Task


class ConceptApiTest(TestCase):
    def setUp(self):
        concept = Concept()
        self.con1 = concept.create("test_view_concept", {"prop": "prop"})
        self.con2 = concept.create("test_view_concept2", {"prop": "prop"})

    def tearDown(self):
        self.con1.delete()
        self.con2.delete()

    def test_conceptapilist(self):
        concept = Concept()
        count = concept.count()
        response = self.client.get(reverse('concept_api_list'))
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), count)
        self.assertEqual(response.status_code, 200)

    def test_conceptapidetail_by_id(self):
        concept = Concept()
        concept.count()
        response = self.client.get(reverse('concept_api_list'), {
                                   'id': self.con1.properties['id']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['name'], "test_view_concept")
        self.assertEqual(response.status_code, 200)

    def test_conceptapidetail_by_name(self):
        concept = Concept()
        concept.count()
        response = self.client.get(reverse('concept_api_list'), {
                                   'name': self.con1.properties['name']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['id'], self.con1.properties['id'])
        self.assertEqual(response.status_code, 200)


class TaskApiTest(TestCase):

    def setUp(self):
        task = Task()
        self.task = task.create(
            "test_view_task", {"prop": "prop", "definition": "definition"})

    def tearDown(self):
        self.task.delete()

    def test_taskapilist(self):
        task = Task()
        count = task.count()
        response = self.client.get(reverse('task_api_list'))
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), count)
        self.assertEqual(response.status_code, 200)

    def test_taskapidetail_by_id(self):
        response = self.client.get(reverse('task_api_list'), {
                                   'id': self.task.properties['id']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['name'], self.task.properties['name'])
        self.assertEqual(response.status_code, 200)

    def test_taskapidetail_by_name(self):
        response = self.client.get(reverse('task_api_list'), {
                                   'name': self.task.properties['name']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['name'], self.task.properties['name'])
        self.assertEqual(response.status_code, 200)


class DisorderApiTest(TestCase):

    def setUp(self):
        disorder = Disorder()
        self.disorder = disorder.create(
            "test_view_disorder", {"prop": "prop", "definition": "definition"})

    def tearDown(self):
        self.disorder.delete()

    def test_disorderapilist(self):
        disorder = Disorder()
        response = self.client.get(reverse('disorder_api_list'))
        count = disorder.count()
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), count)
        self.assertEqual(response.status_code, 200)

    def test_disorderapidetail_by_id(self):
        response = self.client.get(reverse('disorder_api_list'), {
                                   'id': self.disorder.properties['id']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['name'], self.disorder.properties['name'])
        self.assertEqual(response.status_code, 200)

    def test_disorderapidetail_by_name(self):
        response = self.client.get(reverse('disorder_api_list'), {
                                   'name': self.disorder.properties['name']})
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['id'], self.disorder.properties['id'])
        self.assertEqual(response.status_code, 200)


class SearchApiTest(TestCase):
    def setUp(self):
        task = Task()
        self.task = task.create(
            "test_view_task", {"prop": "prop", "definition": "definition"})

    def tearDown(self):
        self.task.delete()

    def testSearchExtant(self):
        response = self.client.get(reverse('search_api_list'), {
                                   'q': self.task.properties['name']})
        self.assertEqual(response.status_code, 200)

    def testSearchNotExtant(self):
        response = self.client.get(reverse('search_api_list'), {
                                   'q': "super silly not existing thing"})
        self.assertEqual(response.status_code, 404)
