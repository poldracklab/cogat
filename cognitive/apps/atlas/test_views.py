import string

from django.core.urlresolvers import reverse
from django.test import TestCase

from cognitive.apps.atlas import views
from cognitive.apps.atlas.query import (Battery, Concept, Condition, Contrast,
                                        Disorder, Task, Theory)

class AtlasViewTestCase(TestCase):

    ''' not currently linked
    def test_all_batteries(self):
        battery = Battery()
        count = battery.count()
        response = self.client.get(reverse('all_batteries'))
        self.assertEqual(response.context['term_type'], 'battery')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)
    '''

    def test_all_concepts(self):
        concept = Concept()
        count = concept.count()
        response = self.client.get(reverse('all_concepts'))
        self.assertEqual(response.context['term_type'], 'concept')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)

    ''' no all contrasts view
    def test_all_contrasts(self):
        contrast = Contrast()
        count = contrast.count()
        response = self.client.get(reverse('all_contrasts'))
        self.assertEqual(response.context['term_type'], 'contrast')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)
    '''

    def test_all_disorders(self):
        disorder = Disorder()
        count = disorder.count()
        response = self.client.get(reverse('all_disorders'))
        self.assertEqual(response.context['active'], 'disorders')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)

    def test_all_tasks(self):
        task = Task()
        count = task.count()
        response = self.client.get(reverse('all_tasks'))
        self.assertEqual(response.context['term_type'], 'task')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)

    def test_all_theories(self):
        theory = Theory()
        count = theory.count()
        response = self.client.get(reverse('all_theories'))
        self.assertEqual(response.context['term_type'], 'theorie')
        self.assertEqual(len(response.context['nodes']), count)

    def test_concepts_by_letter(self):
        for letter in string.ascii_lowercase:
            response = self.client.get(reverse('concepts_by_letter',
                                               kwargs={'letter': letter}))
            self.assertEqual(response.status_code, 200)

    def test_tasks_by_letter(self):
        for letter in string.ascii_lowercase:
            response = self.client.get(reverse('tasks_by_letter',
                                               kwargs={'letter': letter}))
            self.assertEqual(response.status_code, 200)

    def test_view_concept(self):
        concept = Concept()
        con = concept.create("test_view_concept", {"prop": "prop"})
        uid = con.properties['id']
        response = self.client.get(reverse('concept', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['concept']['id'], uid)
        con.delete()

    def test_view_task(self):
        task = Task()
        tsk = task.create("test_view_task",
                          {"prop": "prop", "definition": "definition"})
        uid = tsk.properties['id']
        response = self.client.get(reverse('task', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task']['id'], uid)
        # should also test linked concepts and contrasts
        tsk.delete()

    def test_view_theory(self):
        theory = Theory()
        thry = theory.create("test_view_theory", {"prop": "prop"})
        uid = thry.properties['id']
        response = self.client.get(reverse('theory', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['theory']['id'], uid)
        thry.delete()

    def test_view_disorder(self):
        disorder = Disorder()
        dis = disorder.create("test_view_disorder", {"prop": "prop"})
        uid = dis.properties['id']
        response = self.client.get(reverse('disorder', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['disorder']['id'], uid)
        dis.delete()

    def test_contribute_term(self):
        term_name = 'test_contribute_term'
        response = self.client.post(reverse('contribute_term'),
                                    {'newterm': term_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'],
                         "{}{}".format("Please further define ", term_name))

   # to add: test trying to contribute existing term

    def test_add_term_concept(self):
        concept = Concept()
        concept_name = 'test_add_term_concept'
        definition = 'concept definition'
        response = self.client.post(
            reverse('add_term'),
            {'term_type': 'concept', 'term_name': concept_name,
             'definition_text': definition}
        )
        self.assertEqual(response.status_code, 200)
        uid = response.context['concept']['id']
        con = concept.get(uid)
        self.assertEqual(len(con), 1)
        con = concept.graph.find_one('concept', 'id', uid)
        con.delete()

    def test_add_term_task(self):
        task = Task()
        task_name = 'test_add_term_concept'
        definition = 'task definition'
        response = self.client.post(
            reverse('add_term'),
            {'term_type': 'task', 'term_name': task_name,
             'definition_text': definition}
        )
        self.assertEqual(response.status_code, 200)
        uid = response.context['task']['id']
        tsk = task.get(uid)
        self.assertEqual(len(tsk), 1)
        tsk = task.graph.find_one('task', 'id', uid)
        tsk.delete()

    ''' No URL exists
    def test_contribute_disorder(self):
        response = self.client.get(reverse('contribute_disorder'))
        self.assertEqual(response.status_code, 200)
    '''

    def test_add_condition(self):
        task = Task()
        condition = Condition()
        tsk = task.create("test_add_condition_task",
                          {"prop": "prop", "definition": "definition"})
        uid = tsk.properties['id']
        response = self.client.post(reverse('add_condition', kwargs={'task_id': uid}), {'condition_name': 'test_add_condition'}) 
        self.assertEqual(response.status_code, 200)
        relation = task.get_conditions(uid)
        self.assertEqual(len(relation), 1)
        self.assertEqual(relation[0]['condition_name'], 'test_add_condition')
        con = condition.graph.find_one('condition', 'id', relation[0]['condition_id'])
        tsk.delete_related()
        tsk.delete()
        con.delete()
