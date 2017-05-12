import string

from django.core.urlresolvers import reverse
from django.test import TestCase

from cognitive.apps.atlas import views
from cognitive.apps.atlas.query import (Battery, Concept, Condition, Contrast,
                                        Disorder, Task, Theory)
from cognitive.apps.users.models import User

class AtlasViewTestCase(TestCase):
    def setUp(self):
        self.password = 'pass'
        self.user = User.objects.create_user(
            username='user', email='email@example.com', password=self.password,
            first_name="fn", last_name="ln")

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
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        term_name = 'test_contribute_term'
        response = self.client.post(reverse('contribute_term'),
                                    {'newterm': term_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'],
                         "{}{}".format("Please further define ", term_name))

   # to add: test trying to contribute existing term

    def test_add_term_concept(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
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
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
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
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        condition = Condition()
        tsk = task.create("test_add_condition_task",
                          {"prop": "prop", "definition": "definition"})
        uid = tsk.properties['id']
        response = self.client.post(
            reverse('add_condition', kwargs={'task_id': uid}),
            {'condition_name': 'test_add_condition'}
        )
        self.assertEqual(response.status_code, 200)
        relation = task.get_conditions(uid)
        self.assertEqual(len(relation), 1)
        self.assertEqual(relation[0]['condition_name'], 'test_add_condition')
        con = condition.graph.find_one('condition', 'id', relation[0]['condition_id'])
        tsk.delete_related()
        tsk.delete()
        con.delete()

    def test_update_concept(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        concept = Concept()
        con = concept.create('test_update_concept', {'definition': 'old def'})
        response = self.client.post(
            reverse('update_concept', kwargs={'uid': con.properties['id']}),
            {'definition': 'new def'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual('old def', response.context['concept']['definition'])
        self.assertEqual('new def', response.context['concept']['definition'])
        con.delete()

    def test_update_concept_no_def(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        concept = Concept()
        con = concept.create('test_update_concept', {'prop': 'prop'})
        response = self.client.post(
            reverse('update_concept', kwargs={'uid': con.properties['id']}),
            {'definition': 'new def'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('new def', response.context['concept']['definition'])
        con.delete()

    def test_update_task(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        tsk = task.create('test_update_task', {'prop': 'prop'})
        response = self.client.post(
            reverse('update_task', kwargs={'uid': tsk.properties['id']}),
            {'definition': 'new def'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('new def', response.context['task']['definition'])
        tsk.delete()

    def test_update_theory(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        theory = Theory()
        thry = theory.create('test_update_theory', {'prop': 'prop'})
        response = self.client.post(
            reverse('update_theory', kwargs={'uid': thry.properties['id']}),
            {'theory_name': 'theory_name', 'theory_description': 'theory_description'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('theory_name', response.context['theory']['name'])
        self.assertEqual('theory_description', response.context['theory']['description'])
        thry.delete()

    def test_update_disorder(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        disorder = Disorder()
        dis = disorder.create('test_update_disorder', {'prop': 'prop'})
        response = self.client.post(
            reverse('update_disorder', kwargs={'uid': dis.properties['id']}),
            {'disorder_name': 'disorder_name', 'disorder_definition': 'disorder_definition'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('disorder_name', response.context['disorder']['name'])
        self.assertEqual('disorder_definition', response.context['disorder']['definition'])
        dis.delete()

    def test_add_concept_relation(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        concept = Concept()
        con1 = concept.create('test_update_concept', {'prop': 'prop'})
        con2 = concept.create('test_update_concept', {'prop': 'prop'})
        response = self.client.post(
            reverse('add_concept_relation', kwargs={'uid': con1.properties['id']}),
            {'relation_type': 'PARTOF', 'concept_selection': con2.properties['id']}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['concept']['relations']['PARTOF'][0]['id'], con2.properties['id'])
        con1.delete_related()
        con1.delete()
        con2.delete()

    def test_add_task_contrast(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        condition = Condition()
        tsk = task.create('test_add_task_contrast', {'prop': 'prop'})
        cond1 = condition.create('test_add_task_contrast_cond1', {'prop': 'prop'})
        cond2 = condition.create('test_add_task_contrast_cond2', {'prop': 'prop'})
        cond_names = ['test_add_task_contrast_cond1', 'test_add_task_contrast_cond2'] 
        task.link(tsk.properties['id'], cond1.properties['id'], 'HASCONDITION', endnode_type='condition')
        task.link(tsk.properties['id'], cond2.properties['id'], 'HASCONDITION', endnode_type='condition')
        response = self.client.get(reverse('add_task_contrast',
                                   kwargs={'uid': tsk.properties['id']}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.context['conditions'][0]['condition_name'], cond_names)
        self.assertIn(response.context['conditions'][1]['condition_name'], cond_names)
        self.assertEqual(len(response.context['conditions']), 2)
        tsk.delete_related()
        tsk.delete()
        cond1.delete()
        cond2.delete()

    ''' This view sets up a task -ASSERTS-> concept link and returns task_view 
        task view uses get_contrasts to populate the concepts context variable
        The only way a contrast is found to be associated with a task is by way
        of a condition.
    '''

    def test_add_task_concept(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        concept = Concept()
        contrast = Contrast()
        tsk = task.create('test_add_task_concept', {'prop': 'prop'})
        con = concept.create('test_add_task_concept', {'prop': 'prop'})
        cont = contrast.create('test_add_task_concept', {'prop': 'prop'})
        concept.link(con.properties['id'], cont.properties['id'], "HASCONTRAST", endnode_type='contrast')
        response = self.client.post(
            reverse('add_task_concept', kwargs={'uid': tsk.properties['id']}),
            {'concept_selection': con.properties['id']}
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('task', kwargs={'uid': tsk.properties['id']}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['task']['relations']['ASSERTS']), 1)
        self.assertEqual(response.context['task']['relations']['ASSERTS'][0]['id'],
                         con.properties['id'])
        tsk.delete_related()
        con.delete_related()
        tsk.delete()
        con.delete()
        cont.delete()

    def test_add_concept_contrast(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        condition = Condition()
        task = Task()
        concept = Concept()
        contrast = Contrast()
        cond = condition.create('test_add_concept_contrast', {'prop': 'prop'})
        cont = contrast.create('test_add_task_concept1', {'prop': 'prop'})
        condition.link(cond.properties['id'], cont.properties['id'], "HASCONTRAST", endnode_type='contrast')
        tsk = task.create('test_add_task_concept1', {'prop': 'prop'})
        task.link(tsk.properties['id'], cont.properties['id'], "HASCONTRAST", endnode_type='contrast')
        con = concept.create('test_add_task_concept1', {'prop': 'prop'})
        task.link(tsk.properties['id'], con.properties['id'], "ASSERTS", endnode_type='concept')
        response = self.client.post(
            reverse('add_concept_contrast', kwargs={'uid': tsk.properties['id']}),
            {'contrast_selection': cont.properties['id'], 'concept_id': con.properties['id']}
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('task', kwargs={'uid': tsk.properties['id']}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['task']['relations']['ASSERTS']), 1)
        tsk.delete_related()
        con.delete_related()
        tsk.delete()
        con.delete()
        cont.delete()

    def test_add_task_implementation(self):
        pass
