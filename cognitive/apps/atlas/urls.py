from django.conf.urls import url

from rest_framework.authtoken import views as drf_views

from . import api_views, views, graph


urlpatterns = [
    # List views
    url(r'^concepts$', views.all_concepts, name="all_concepts"),
    url(r'^concepts/categories/all$', views.all_concept_classes,
        name="all_concept_classes"),
    url(r'^disorders$', views.all_disorders, name="all_disorders"),
    url(r'^batteries$', views.all_batteries, name="all_batteries"),
    url(r'^theories$', views.all_theories, name="all_theories"),
    url(r'^tasks$', views.all_tasks, name="all_tasks"),
    url(r'^collections/$', views.all_collections, name="all_collections"),

    # Search (json response) views
    url(r'^search$', views.search_all, name="search"),
    url(r'^concepts/search$', views.search_concept, name="search_concept"),
    url(r'^tasks/search$', views.search_task, name="search_task"),
    url(r'^contrasts/search$', views.search_contrast, name="search_contrast"),

    # View by letter
    url(r'^concepts/(?P<letter>[a-z]|[A-Z]{1})/$', views.concepts_by_letter,
        name="concepts_by_letter"),
    url(r'^tasks/(?P<letter>[a-z]|[A-Z]{1})/$', views.tasks_by_letter,
        name="tasks_by_letter"),

    # Detail View
    url(r'^id/(?P<uid>[\w\+%_& ]+)/$', views.view_term, name="view_term"),
    url(r'^contrast/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_contrast, name="view_contrast"),
    url(r'^disorder/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_disorder, name="disorder"),
    url(r'^disorder/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_disorder, name="view_disorder"),
    url(r'^trait/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_trait, name="view_trait"),
    url(r'^behavior/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_behavior, name="view_behavior"),
    url(r'^battery/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_battery, name="battery"),
    url(r'^battery/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_battery, name="view_battery"),
    url(r'^theory/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_theory, name="theory"),
    url(r'^theory/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_theory, name="view_theory"),
    url(r'^concept/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_concept, name="concept"),
    url(r'^concept/id/(?P<uid>[\w\+%_& ]+)/$',
        views.view_concept, name="view_concept"),
    url(r'^task/id/(?P<uid>[\w\+%_& ]+)/$', views.view_task, name="task"),
    url(r'^task/id/(?P<uid>[\w\+%_& ]+)/$', views.view_task, name="view_task"),
    url(r'^contrast/id/(?P<uid>[\w\+%_& ]+)/$',
        graph.contrast_gist, name="contrast"),
    url(r'^contrast/id/(?P<uid>[\w\+%_& ]+)/$',
        graph.contrast_gist, name="view_contrast"),
    url(r'^disambiguation/id/(?P<uid>[\w\+%_& ]+)/$', views.view_disambiguation,
        name="view_disambiguation"),

    # Modify terms
    url(r'^terms/new/$', views.contribute_term, name="contribute_term"),
    url(r'^disorder/new/$',
        views.contribute_disorder,
        name="contribute_disorder"),
    url(r'^phenotype/new/$', views.add_phenotype, name="add_phenotype"),
    url(r'^theory/new/$', views.add_theory, name="add_theory"),
    url(r'^battery/new/$', views.add_battery, name="add_battery"),
    url(r'^terms/add/$', views.add_term, name="add_term"),
    url(r'^concepts/categories/add$',
        views.add_concept_class, name="add_concept_class"),
    url(r'^concept/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_concept, name="update_concept"),
    url(r'^task/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_task, name="update_task"),
    url(r'^disorder/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_disorder, name="update_disorder"),
    url(r'^trait/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_trait, name="update_trait"),
    url(r'^behavior/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_behavior, name="update_behavior"),
    url(r'^theory/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_theory, name="update_theory"),
    url(r'^battery/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_battery, name="update_battery"),
    url(r'^contrast/update/(?P<uid>[\w\+%_& ]+)/$',
        views.update_contrast, name="update_contrast"),
    url(r'^concept/assert/(?P<uid>[\w\+%_& ]+)/$', views.add_concept_relation,
        name="add_concept_relation"),
    url(r'^task/add/concept/(?P<uid>[\w\+%_& ]+)/$', views.add_task_concept,
        name="add_task_concept"),
    url(r'^concept/add/contrast/(?P<uid>[\w\+%_& ]+)/$', views.add_concept_contrast_task,
        name="add_concept_contrast_task"),
    url(r'^task/add/contrast/(?P<uid>[\w\+%_& ]+)/$', views.add_task_contrast,
        name="add_task_contrast"),
    url(r'^contrast/add/(?P<uid>[\w\+%_& ]+)/$',
        views.add_contrast, name="add_contrast"),
    url(r'^condition/add/(?P<uid>[\w\+%_& ]+)/$',
        views.add_condition, name="add_condition"),
    url(
        r'^task/add/implementation/(?P<uid>[\w\+%_& ]+)/$',
        views.add_task_implementation,
        name="add_task_implementation"
    ),
    url(
        r'^task/add/dataset/(?P<uid>[\w\+%_& ]+)/$',
        views.add_task_dataset,
        name="add_task_dataset"
    ),
    url(
        r'^task/add/indicator/(?P<uid>[\w\+%_& ]+)/$',
        views.add_task_indicator,
        name="add_task_indicator"
    ),
    url(
        r'^task/add/disorder/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_disorder,
        name="add_task_disorder"
    ),
    url(
        r'^concept/add/task/(?P<concept_id>[\w\+%_& ]+)/$',
        views.add_concept_task,
        name="add_concept_task"
    ),
    url(
        r'^disorder/add/task/(?P<uid>[\w\+%_& ]+)/$',
        views.add_disorder_task,
        name="add_disorder_task"
    ),
    url(
        r'^theory/add/assertion/(?P<theory_id>[\w\+%_& ]+)/$',
        views.add_theory_assertion,
        name="add_theory_assertion"
    ),
    url(
        r'^concept/add/contrast/(?P<uid>[\w\+%_& ]+)/$',
        views.add_concept_contrast,
        name="add_concept_contrast"
    ),
    url(
        r'^disorder/add/disorder/(?P<disorder_id>[\w\+%_& ]+)/$',
        views.add_disorder_disorder,
        name="add_disorder_disorder"
    ),
    url(
        r'^disorder/add/link/(?P<uid>[\w\+%_& ]+)/$',
        views.add_disorder_external_link,
        name="add_disorder_external_link"
    ),
    url(
        r'^battery/add/indicator/(?P<battery_id>[\w\+%_& ]+)/$',
        views.add_battery_indicator,
        name="add_battery_indicator"
    ),
    url(
        r'^battery/add/battery/(?P<uid>[\w\+%_& ]+)/$',
        views.add_battery_battery,
        name="add_battery_battery"
    ),
    url(
        r'^battery/add/task/(?P<uid>[\w\+%_& ]+)/$',
        views.add_battery_task,
        name="add_battery_task"
    ),
    url(
        r'^trait/add/contrast/(?P<uid>[\w\+%_& ]+)/$',
        views.add_trait_contrast,
        name="add_trait_contrast"
    ),
    url(
        r'^disorder/add/contrast/(?P<uid>[\w\+%_& ]+)/$',
        views.add_disorder_contrast,
        name="add_disorder_contrast"
    ),
    url(
        r'^behavior/add/contrast/(?P<uid>[\w\+%_& ]+)/$',
        views.add_behavior_contrast,
        name="add_behavior_contrast"
    ),
    url(
        r'^disambiguation/add/(?P<label>[\w]+)/(?P<uid>[\w\+%_& ]+)/$',
        views.add_disambiguation,
        name="add_disambiguation"
    ),
    url(
        r'^(?P<label>[\w]+)/add/doi/(?P<uid>[\w\+%_& ]+)/$',
        views.add_citation_doi,
        name="add_citation_doi"
    ),
    url(
        r'^(?P<label>[\w]+)/unlink/doi/(?P<uid>[\w\+%_& ]+)/(?P<cid>[\w\+%_& ]+)/$',
        views.unlink_citation,
        name="unlink_citation"
    ),

    url(
        r'^disambiguation/link/(?P<label>[\w]+)/(?P<uid>[\w\+%_& ]+)/$',
        views.link_disam,
        name="link_disam"
    ),
    url(
        r'^disambiguation/unlink/(?P<label>[\w]+)/(?P<uid>[\w\+%_& ]+)/(?P<tid>[\w\+%_& ]+)$',
        views.unlink_disam,
        name="unlink_disam"
    ),

    url(r'^reviewed/(?P<label>[\w]+)/(?P<uid>[\w\+%_& ]+)/$',
        views.set_reviewed, name="set_reviewed"),
    url(r'^unreviewed/(?P<label>[\w]+)/(?P<uid>[\w\+%_& ]+)/$',
        views.set_unreviewed, name="set_unreviewed"),

    # Graph views
    url(r'^graph/(?P<label>[\w\+])/(?P<uid>[\w\+%_& ]+)', graph.graph_view,
        name="graph_view"),
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)', graph.graph_view,
        {'label': 'task'}, name="task_graph"),
    url(r'^graph/concept/(?P<uid>[\w\+%_& ]+)', graph.graph_view,
        {'label': 'concept'}, name="concept_graph"),
]

api_urls = [
    url(r'^api/search$', api_views.SearchAPI.as_view(), name='search_api_list'),
    url(r'^api/concept$',
        api_views.ConceptAPI.as_view(),
        name='concept_api_list'),
    url(r'^api/task$', api_views.TaskAPI.as_view(), name='task_api_list'),
    url(r'^api/disorder$',
        api_views.DisorderAPI.as_view(),
        name='disorder_api_list'),
    url(r'^api/v-alpha/search$',
        api_views.SearchAPI.as_view(), name='search_api_list'),
    url(r'^api/v-alpha/concept$',
        api_views.ConceptAPI.as_view(), name='concept_api_list'),
    url(r'^api/v-alpha/task$',
        api_views.TaskAPI.as_view(),
        name='task_api_list'),
    url(r'^api/v-alpha/disorder', api_views.DisorderAPI.as_view(),
        name='disorder_api_list'),
    url(r'^task/json/(?P<uid>[\w\+%_& ]+)/$',
        graph.task_json, name="task_json"),
    url(r'^concept/json/(?P<uid>[\w\+%_& ]+)/$',
        graph.concept_json, name="concept_json"),
    url(
        r'^api/task/(?P<uid>[\w\+%_& ]+)/contrast$',
        api_views.ContrastAPI.as_view(),
        name='contrast_api'
    ),
    url(
        r'^api/task/(?P<uid>[\w\+%_& ]+)/condition$',
        api_views.ConditionAPI.as_view(),
        name='contrast_api'
    ),
    url(r'^api/concept/relate/$', api_views.ConceptRelAPI.as_view(),
        name="add_concept_relation_api"),
    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/concept/$', api_views.TaskConceptAPI.as_view(),
        name="add_task_concept_api"),

    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/disorder/$', api_views.TaskDisorderAPI.as_view(),
        name="add_task_disorder_api"),
    url(r'^api/disorder/(?P<uid>[\w\+%_& ]+)/disorder/$', api_views.DisorderDisorderAPI.as_view(),
        name="add_disorder_disorder_api"),
    url(r'^api/disorder/(?P<uid>[\w\+%_& ]+)/citation/$',
        api_views.DisorderCitationAPI.as_view(), name="add_disorder_citation_api"),
    url(r'^api/disorder/(?P<uid>[\w\+%_& ]+)/ExternalLink/$',
        api_views.DisorderExternalLinkAPI.as_view(), name="add_disorder_external_link_api"),
    url(r'^api/disorder/(?P<uid>[\w\+%_& ]+)/task/$',
        api_views.DisorderTask.as_view(), name="add_disorder_task_api"),

    url(r'^api/concept/(?P<uid>[\w\+%_& ]+)_/contrast$',
        api_views.ConceptContrastAPI.as_view(), name="add_concept_contrast_api"),
    url(r'^api/concept/(?P<uid>[\w\+%_& ]+)/contrast/task$',
        api_views.ConceptContrastTaskAPI.as_view(), name="add_concept_contrast_task_api"),
    url(r'^api/concept/(?P<uid>[\w\+%_& ]+)/citation/$',
        api_views.ConceptCitationAPI.as_view(), name="add_concept_citation_api"),

    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/implementation/$',
        api_views.TaskImplementationAPI.as_view(), name="add_task_implementation_api"),
    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/dataset/$',
        api_views.TaskDatasetAPI.as_view(), name="add_task_dataset_api"),
    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/indicator/$',
        api_views.TaskIndicatorAPI.as_view(), name="add_task_indicator_api"),
    url(r'^api/task/(?P<uid>[\w\+%_& ]+)/citation/$',
        api_views.TaskCitationAPI.as_view(), name="add_task_citation_api"),

    url(r'^api/battery/(?P<uid>[\w\+%_& ]+)/citation/$',
        api_views.BatteryCitationAPI.as_view(), name="add_battery_citation_api"),
    url(r'^api/battery/(?P<uid>[\w\+%_& ]+)/indicator/$',
        api_views.BatteryIndicatorAPI.as_view(), name="add_battery_indicator_api"),
    url(r'^api/battery/(?P<uid>[\w\+%_& ]+)/battery/$',
        api_views.BatteryBatteryAPI.as_view(), name="add_battery_battery_api"),
    url(r'^api/battery/(?P<uid>[\w\+%_& ]+)/task/$',
        api_views.BatteryTaskAPI.as_view(), name="add_battery_task_api"),
    url(r'^api/battery$',
        api_views.BatteryAPI.as_view(), name="battery_list_api"),

    url(r'^api/theory$', api_views.TheoryAPI.as_view(), name="theory_list_api"),
    url(r'^api/user$', api_views.UserAPI.as_view(), name="user_list_api"),
    url(r'^api/theory/(?P<uid>[\w\+%_& ]+)/assertion/$',
        api_views.TheoryAssertion.as_view(), name="add_theory_assertion_api"),
    url(r'^api/theory/(?P<uid>[\w\+%_& ]+)/citation/$',
        api_views.TheoryCitationAPI.as_view(), name="add_theory_citation_api"),
    url(r'^api-token-auth/', drf_views.obtain_auth_token),

]

urlpatterns += api_urls
