from django.urls import resolve
from django.test import TestCase


class AtlasUrlTestCase(TestCase):
    def test_all_concepts(self):
        found = resolve('/concepts')
        self.assertEqual(found.view_name, 'all_concepts')

    def test_all_tasks(self):
        found = resolve('/tasks')
        self.assertEqual(found.view_name, 'all_tasks')

    def test_all_batteries(self):
        found = resolve('/batteries')
        self.assertEqual(found.view_name, 'all_batteries')

    def test_all_theories(self):
        found = resolve('/theories')
        self.assertEqual(found.view_name, 'all_theories')

    def test_all_disorders(self):
        found = resolve('/disorders')
        self.assertEqual(found.view_name, 'all_disorders')

    def test_concepts_by_letter(self):

        found = resolve('/concepts/a/')
        self.assertEqual(found.view_name, 'concepts_by_letter')

    def test_tasks_by_letter(self):
        found = resolve('/tasks/a/')
        self.assertEqual(found.view_name, 'tasks_by_letter')

    def test_view_concept(self):
        found = resolve('/concept/id/fake_123/')
        self.assertEqual(found.view_name, 'concept')

    def test_view_task(self):
        found = resolve('/task/id/fake_123/')
        self.assertEqual(found.view_name, 'task')

    def test_view_battery(self):
        found = resolve('/battery/id/fake_123/')
        self.assertEqual(found.view_name, 'battery')

    def test_view_theory(self):
        found = resolve('/theory/id/fake_123/')
        self.assertEqual(found.view_name, 'theory')

    def test_view_disorder(self):
        found = resolve('/disorder/id/fake_123/')
        self.assertEqual(found.view_name, 'disorder')

    def test_contribute_term(self):
        found = resolve('/terms/new/')
        self.assertEqual(found.view_name, 'contribute_term')

    def test_add_term(self):
        found = resolve('/terms/add/')
        self.assertEqual(found.view_name, 'add_term')

    def test_update_concept(self):
        found = resolve('/concept/update/fake_123/')
        self.assertEqual(found.view_name, 'update_concept')

    def test_update_task(self):
        found = resolve('/task/update/fake_123/')
        self.assertEqual(found.view_name, 'update_task')

    def test_update_theory(self):
        found = resolve('/theory/update/fake_123/')
        self.assertEqual(found.view_name, 'update_theory')

    def test_update_disorder(self):
        found = resolve('/disorder/update/fake_123/')
        self.assertEqual(found.view_name, 'update_disorder')

    def test_add_concept_relation(self):
        found = resolve('/concept/assert/fake_123/')
        self.assertEqual(found.view_name, 'add_concept_relation')

    def test_add_task_contrast(self):
        found = resolve('/task/add/contrast/fake_123/')
        self.assertEqual(found.view_name, 'add_task_contrast')

    def test_add_task_concept(self):
        found = resolve('/task/add/concept/fake_123/')
        self.assertEqual(found.view_name, 'add_task_concept')

    def test_add_concept_contrast(self):
        found = resolve('/concept/add/contrast/fake_123/')
        self.assertEqual(found.view_name, 'add_concept_contrast_task')

    def test_add_contrast(self):
        found = resolve('/contrast/add/fake_123/')
        self.assertEqual(found.view_name, 'add_contrast')

    def test_add_condition(self):
        found = resolve('/condition/add/fake_123/')
        self.assertEqual(found.view_name, 'add_condition')

    def test_search_all(self):
        found = resolve('/search')
        self.assertEqual(found.view_name, 'search')

    def test_search_concept(self):
        found = resolve('/concepts/search')
        self.assertEqual(found.view_name, 'search_concept')

    '''
    # Graph views
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/$', graph.task_graph, name="task_graph"),
    url(r'^graph/concept/(?P<uid>[\w\+%_& ]+)/$', graph.concept_graph, name="concept_graph"),
    url(r'^graph/$', graph.explore_graph, name="explore_graph"),
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/gist$', graph.task_gist, name="task_gist"),
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/gist/download$', graph.download_task_gist, name="download_task_gist"),
    '''
