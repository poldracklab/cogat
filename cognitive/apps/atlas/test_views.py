import string

from django.urls import reverse
from django.test import TestCase

from cognitive.apps.atlas.forms import ConceptForm
from cognitive.apps.atlas.query import (Assertion, Concept, Condition,
                                        Contrast, Disorder, Task, Theory)
from cognitive.apps.users.models import User
from cognitive.settings import graph

class AtlasViewTestCase(TestCase):
    def setUp(self):
        self.password = 'pass'
        self.user = User.objects.create_user(
            username='user', email='email@example.com', password=self.password,
            first_name="fn", last_name="ln", rank="3")

    def tearDown(self):
        graph.delete_all()

    def make_task(self, name='test_task', definition='task definition'):
        task = Task()
        definition = 'task definition'
        response = self.client.post(
            reverse('add_term'),
            {'term_type': 'task', 'term_name': name,
             'definition_text': definition},
            follow=True
        )
        return task.get_full(name, 'name')['id']

    def make_concept(self, name='test_concept', definition='definition'):
        concept = Concept()
        post_kwargs = {'term_type': 'concept', 'term_name': name}
        if definition:
            post_kwargs['definition_text'] = definition
        response = self.client.post(
            reverse('add_term'),
            post_kwargs,
            follow=True
        )
        return concept.get_full(name, 'name')['id']

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

    ''' Can't count all, need a count from disorder populate
    def test_all_disorders(self):
        disorder = Disorder()
        count = disorder.count()
        response = self.client.get(reverse('all_disorders'))
        self.assertEqual(response.context['active'], 'disorders')
        self.assertEqual(len(response.context['disorders']), count)
        self.assertEqual(response.status_code, 200)
    '''

    def test_all_tasks(self):
        task = Task()
        count = task.count()
        response = self.client.get(reverse('all_tasks'))
        self.assertEqual(response.context['term_type'], 'task')
        self.assertEqual(len(response.context['nodes']), count)
        self.assertEqual(response.status_code, 200)

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
        uid = con['id']
        response = self.client.get(reverse('concept', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['concept']['id'], uid)
        graph.delete(con)

    def test_view_task(self):
        task = Task()
        tsk = task.create("test_view_task",
                          {"prop": "prop", "definition": "definition"})
        uid = tsk['id']
        response = self.client.get(reverse('task', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task']['id'], uid)
        # should also test linked concepts and contrasts
        graph.delete(tsk)

    def test_view_theory(self):
        theory = Theory()
        thry = theory.create("test_view_theory", {"prop": "prop"})
        uid = thry['id']
        response = self.client.get(reverse('theory', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['theory']['id'], uid)
        graph.delete(thry)

    def test_view_disorder(self):
        disorder = Disorder()
        dis = disorder.create("test_view_disorder", {"prop": "prop"})
        uid = dis['id']
        response = self.client.get(reverse('disorder', kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['disorder']['id'], uid)
        graph.delete(dis)

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
             'definition_text': definition},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        uid = response.context['concept']['id']
        con = graph.nodes.match('concept', id=uid).first()
        self.assertNotEqual(con, None)
        

    def test_add_term_task(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        task_name = 'test_add_term_task'
        definition = 'task definition'
        response = self.client.post(
            reverse('add_term'),
            {'term_type': 'task', 'term_name': task_name,
             'definition_text': definition},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        uid = response.context['task']['id']
        tsk = task.get(uid)
        self.assertEqual(len(tsk), 1)
        

    ''' No URL exists
    def test_contribute_disorder(self):
        response = self.client.get(reverse('contribute_disorder'))
        self.assertEqual(response.status_code, 200)
    '''

    def test_add_condition(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        task_name = 'test_add_term_concept'
        definition = 'task definition'
        uid = self.make_task(task_name, definition)

        response = self.client.post(
            reverse('add_condition', kwargs={'uid': uid}),
            {'condition_name': 'test_add_condition'}
        )
        self.assertEqual(response.status_code, 200)
        relation = task.get_conditions(uid)
        self.assertEqual(len(relation), 1)
        self.assertEqual(relation[0]['condition_name'], 'test_add_condition')
        graph.delete(graph.nodes.match("task", id=uid).first())
        graph.delete(graph.nodes.match("condition").first())

    def test_update_concept(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        uid = self.make_concept('test_add_term_concept', 'old def')
        concept = Concept()
        con = concept.get(uid)[0]
        con['definition_text'] = 'new def'
        response = self.client.post(
            reverse('update_concept', kwargs={'uid': uid}),
            con, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            'old def', response.context['concept']['definition_text'])
        self.assertEqual(
            'new def', response.context['concept']['definition_text'])
        

    def test_update_concept_no_def(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        uid = self.make_concept('test_add_term_concept', None)
        concept = Concept()
        con = concept.get(uid)[0]
        con['definition_text'] = 'new def'
        response = self.client.post(
            reverse('update_concept', kwargs={'uid': uid}),
            con, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            'new def', response.context['concept']['definition_text'])
        

    def test_update_task(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        uid = self.make_task('add_task_dataset')
        response = self.client.post(
            reverse('update_task', kwargs={'uid': uid}),
            {'definition_text': 'new def'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            'new def', response.context['task']['definition_text'])
        

    def test_update_theory(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        theory = Theory()
        response = self.client.post(
            reverse('add_theory'),
            {'name': 'theory_has_a_name',
             'collection_description': 'theory has a definition'},
            follow=True
        )
        uid = theory.get('theory_has_a_name', 'name')[0]['id']

        response = self.client.post(
            reverse('update_theory', kwargs={'uid': uid}),
            {'theory_name': 'theory_name',
             'collection_description': 'theory_description'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('theory_name', response.context['theory']['name'])
        self.assertEqual('theory_description',
                         response.context['theory']['collection_description'])

    def test_update_disorder(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        disorder = Disorder()
        response = self.client.post(
            reverse('contribute_disorder'),
            {'name': 'disorder_name',
             'definition': 'disorder_definition'},
            follow=True
        )
        uid = disorder.get('disorder_name', 'name')[0]['id']


        response = self.client.post(
            reverse('update_disorder', kwargs={'uid': uid}),
            {'disorder_name': 'disorder_name',
                'disorder_definition': 'disorder_definition'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('disorder_name', response.context['disorder']['name'])
        self.assertEqual('disorder_definition',
                         response.context['disorder']['definition'])
        

    def test_add_concept_relation(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        concept = Concept()
        con1_uid = self.make_concept()
        con2_uid = self.make_concept()
        response = self.client.post(
            reverse('add_concept_relation', kwargs={
                    'uid': con1_uid}),
            {'relation_type': 'PARTOF',
                'concept_selection': con2_uid}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['concept']['relations']['PARTOF'][0]['id'], con2_uid)
        

    ''' this is only testing if conditions show up as options in the form to
        create contrast for a task. Should be extended to actually add contrast
    '''
    def test_add_task_contrast(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        uid = self.make_task()
        cond_names = ['test_add_task_contrast_cond1', 'test_add_task_contrast_cond2']

        response = self.client.post(
            reverse('add_condition', kwargs={'uid': uid}),
            {'condition_name': cond_names[0]}
        )
        response = self.client.post(
            reverse('add_condition', kwargs={'uid': uid}),
            {'condition_name': cond_names[1]}
        )

        response = self.client.get(reverse('add_task_contrast',
                                           kwargs={'uid': uid}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.context['conditions']
                      [0]['condition_name'], cond_names)
        self.assertIn(response.context['conditions']
                      [1]['condition_name'], cond_names)
        self.assertEqual(len(response.context['conditions']), 2)
        

    def test_add_task_concept(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        concept = Concept()
        contrast = Contrast()
        tsk = task.create('test_add_task_concept', {'prop': 'prop'})
        con = concept.create('test_add_task_concept', {'prop': 'prop'})
        cont = contrast.create('test_add_task_concept', {'prop': 'prop'})
        task.link(tsk['id'], cont['id'],
                     "HASCONTRAST", endnode_type='contrast')
        response = self.client.post(
            reverse('add_task_concept', kwargs={'uid': tsk['id']}),
            {'concept_selection': con['id']}
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('task', kwargs={'uid': tsk['id']}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['task']['relations']['HASCONTRAST']), 1)
        self.assertEqual(response.context['task']['relations']['HASCONTRAST'][0]['id'],
                         cont['id'])
        

    ''' dispabled for the time being. Want all concept-contrast relations to happen in task view
    def test_add_concept_contrast(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        condition = Condition()
        task = Task()
        concept = Concept()
        contrast = Contrast()
        cond = condition.create('test_add_concept_contrast', {'prop': 'prop'})
        cont = contrast.create('test_add_task_concept1', {'prop': 'prop'})
        condition.link(cond['id'], cont['id'], "HASCONTRAST", endnode_type='contrast')
        tsk = task.create('test_add_task_concept1', {'prop': 'prop'})
        task.link(tsk['id'], cont['id'], "HASCONTRAST", endnode_type='contrast')
        con = concept.create('test_add_task_concept1', {'prop': 'prop'})
        task.link(tsk['id'], con['id'], "ASSERTS", endnode_type='concept')
        response = self.client.post(
            reverse('add_concept_contrast', kwargs={'uid': tsk['id']}),
            {'contrast_selection': cont['id'], 'concept_id': con['id']}
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('task', kwargs={'uid': tsk['id']}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['task']['relations']['ASSERTS']), 1)
        graph.delete(tsk)
        graph.delete(con)
        graph.delete(cont)
    '''

    def test_add_task_implementation(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        uid = self.make_task('add_task_dataset')
        data = {
            'implementation_uri': 'http://example.com',
            'implementation_name': 'add_task_implementation',
            'implementation_description': 'task imp desc'
        }
        response = self.client.post(
            reverse('add_task_implementation', kwargs={
                    'uid': uid}),
            data
        )
        self.assertEqual(response.status_code, 200)
        imp = task.get_relation(uid, "HASIMPLEMENTATION")
        self.assertEqual(len(imp), 1)
        self.assertEqual(imp[0]['name'], 'add_task_implementation')
        

    def test_add_task_dataset(self):
        task = Task()
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        uid = self.make_task('add_task_dataset')
        data = {
            'dataset_uri': 'http://example.com',
            'dataset_name': 'add_task_dataset',
        }
        response = self.client.post(
            reverse('add_task_dataset', kwargs={
                    'uid': uid}),
            data
        )
        self.assertEqual(response.status_code, 200)
        ds = task.get_relation(uid, "HASEXTERNALDATASET")
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]['name'], 'add_task_dataset')
        

    def test_add_task_indicator(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        task = Task()
        uid = self.make_task('add_task_dataset')
        data = {
            'type': 'add_task_indicator',
        }
        response = self.client.post(
            reverse('add_task_indicator', kwargs={
                    'uid': uid}),
            data
        )
        self.assertEqual(response.status_code, 200)
        ind = task.get_relation(uid, "HASINDICATOR")
        self.assertEqual(len(ind), 1)
        self.assertEqual(ind[0]['name'], 'add_task_indicator')
        

    '''
    def test_add_theory_assertion(self):
        Asrt = Assertion()
        Thry = Theory()
        assertion = Asrt.create('test_add_theory_assertion')
        theory = Thry.create('test_add_theory_assertion')
        data = {
            'assertions': assertion['id']
        }

        self.assertTrue(self.client.login(
            username=self.user.username, password=self.password))
        response = self.client.post(
            reverse('add_theory_assertion',
                    kwargs={'theory_id': theory['id']}), data
        )
        self.assertEqual(response.status_code, 200)
        thry = Asrt.get_relation(assertion['id'], "INTHEORY")
        self.assertEqual(thry[0]['name'], 'test_add_theory_assertion')
        graph.delete(theory)
        graph.delete(assertion)
    '''
