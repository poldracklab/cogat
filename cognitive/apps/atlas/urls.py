from django.conf.urls import url

from . import api_views, views, graph


urlpatterns = [
    # List views
    url(r'^concepts$', views.all_concepts, name="all_concepts"),
    url(r'^disorders$', views.all_disorders, name="all_disorders"),
    url(r'^batteries$', views.all_batteries, name="all_batteries"),
    url(r'^theories$', views.all_theories, name="all_theories"),
    url(r'^tasks$', views.all_tasks, name="all_tasks"),
    url(r'^collections/$', views.all_collections, name="all_collections"),

    # Search (json response) views
    url(r'^search$', views.search_all, name="search"),
    url(r'^concepts/search$', views.search_concept, name="search_concept"),
    url(r'^tasks/search$', views.search_task, name="search_task"),

    # View by letter
    url(r'^concepts/(?P<letter>[a-z]|[A-Z]{1})/$', views.concepts_by_letter,
        name="concepts_by_letter"),
    url(r'^tasks/(?P<letter>[a-z]|[A-Z]{1})/$', views.tasks_by_letter,
        name="tasks_by_letter"),

    # Detail View
    url(r'^disorder/id/(?P<uid>[\w\+%_& ]+)/$', views.view_disorder, name="disorder"),
    url(r'^battery/id/(?P<uid>[\w\+%_& ]+)/$', views.view_battery, name="battery"),
    url(r'^theory/id/(?P<uid>[\w\+%_& ]+)/$', views.view_theory, name="theory"),
    url(r'^concept/id/(?P<uid>[\w\+%_& ]+)/$', views.view_concept, name="concept"),
    url(r'^task/id/(?P<uid>[\w\+%_& ]+)/$', views.view_task, name="task"),
    url(r'^contrast/id/(?P<uid>[\w\+%_& ]+)/$', graph.contrast_gist, name="contrast"),

    # Modify terms
    url(r'^terms/new/$', views.contribute_term, name="contribute_term"),
    url(r'^disorder/new/$', views.contribute_disorder, name="contribute_disorder"),
    url(r'^theory/new/$', views.add_theory, name="add_theory"),
    url(r'^battery/new/$', views.add_battery, name="add_battery"),
    url(r'^terms/add/$', views.add_term, name="add_term"),
    url(r'^concept/update/(?P<uid>[\w\+%_& ]+)/$', views.update_concept, name="update_concept"),
    url(r'^task/update/(?P<uid>[\w\+%_& ]+)/$', views.update_task, name="update_task"),
    url(r'^disorder/update/(?P<uid>[\w\+%_& ]+)/$', views.update_disorder, name="update_disorder"),
    url(r'^theory/update/(?P<uid>[\w\+%_& ]+)/$', views.update_theory, name="update_theory"),
    url(r'^battery/update/(?P<uid>[\w\+%_& ]+)/$', views.update_battery, name="update_battery"),
    url(r'^concept/assert/(?P<uid>[\w\+%_& ]+)/$', views.add_concept_relation,
        name="add_concept_relation"),
    url(r'^task/add/concept/(?P<uid>[\w\+%_& ]+)/$', views.add_task_concept,
        name="add_task_concept"),
    url(r'^concept/add/contrast/(?P<uid>[\w\+%_& ]+)/$', views.add_concept_contrast_task,
        name="add_concept_contrast_task"),
    url(r'^task/add/contrast/(?P<uid>[\w\+%_& ]+)/$', views.add_task_contrast,
        name="add_task_contrast"),
    url(r'^contrast/add/(?P<task_id>[\w\+%_& ]+)/$', views.add_contrast, name="add_contrast"),
    url(r'^condition/add/(?P<task_id>[\w\+%_& ]+)/$', views.add_condition, name="add_condition"),
    url(
        r'^task/add/implementation/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_implementation,
        name="add_task_implementation"
    ),
    url(
        r'^task/add/dataset/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_dataset,
        name="add_task_dataset"
    ),
    url(
        r'^task/add/indicator/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_indicator,
        name="add_task_indicator"
    ),
    url(
        r'^task/add/citation/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_citation,
        name="add_task_citation"
    ),
    url(
        r'^task/add/disorder/(?P<task_id>[\w\+%_& ]+)/$',
        views.add_task_disorder,
        name="add_task_disorder"
    ),
    url(
        r'^concept/add/citation/(?P<concept_id>[\w\+%_& ]+)/$',
        views.add_concept_citation,
        name="add_concept_citation"
    ),
    url(
        r'^disorder/add/citation/(?P<disorder_id>[\w\+%_& ]+)/$',
        views.add_disorder_citation,
        name="add_disorder_citation"
    ),
    url(
        r'^concept/add/task/(?P<concept_id>[\w\+%_& ]+)/$',
        views.add_concept_task,
        name="add_concept_task"
    ),
    url(
        r'^disorder/add/task/(?P<disorder_id>[\w\+%_& ]+)/$',
        views.add_disorder_task,
        name="add_disorder_task"
    ),
    url(
        r'^theory/add/assertion/(?P<theory_id>[\w\+%_& ]+)/$',
        views.add_theory_assertion,
        name="add_theory_assertion"
    ),
    url(
        r'^theory/add/citation/(?P<theory_id>[\w\+%_& ]+)/$',
        views.add_theory_citation,
        name="add_theory_citation"
    ),
    url(
        r'^battery/add/citation/(?P<battery_id>[\w\+%_& ]+)/$',
        views.add_battery_citation,
        name="add_battery_citation"
    ),
    url(
        r'^concept/add/contrast/(?P<uid>[\w\+%_& ]+)/(?P<tid>[\w\+%_& ]+)/$',
        views.add_concept_contrast,
        name="add_concept_contrast"
    ),
    url(
        r'^disorder/add/disorder/(?P<disorder_id>[\w\+%_& ]+)/$',
        views.add_disorder_disorder,
        name="add_disorder_disorder"
    ),
    url(
        r'^disorder/add/link/(?P<disorder_id>[\w\+%_& ]+)/$',
        views.add_disorder_external_link,
        name="add_disorder_external_link"
    ),

    # Graph views
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/$', graph.task_graph, name="task_graph"),
    url(r'^graph/concept/(?P<uid>[\w\+%_& ]+)/$', graph.concept_graph, name="concept_graph"),
    url(r'^graph/$', graph.explore_graph, name="explore_graph"),
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/gist$', graph.task_gist, name="task_gist"),
    url(r'^graph/task/(?P<uid>[\w\+%_& ]+)/gist/download$', graph.download_task_gist,
        name="download_task_gist"),
]

api_urls = [
    url(r'^api/search$', api_views.SearchAPI.as_view(), name='search_api_list'),
    url(r'^api/concept$', api_views.ConceptAPI.as_view(), name='concept_api_list'),
    url(r'^api/task$', api_views.TaskAPI.as_view(), name='task_api_list'),
    url(r'^api/disorder', api_views.DisorderAPI.as_view(), name='disorder_api_list'),
    url(r'^api/v-alpha/search$', api_views.SearchAPI.as_view(), name='search_api_list'),
    url(r'^api/v-alpha/concept$', api_views.ConceptAPI.as_view(), name='concept_api_list'),
    url(r'^api/v-alpha/task$', api_views.TaskAPI.as_view(), name='task_api_list'),
    url(r'^api/v-alpha/disorder', api_views.DisorderAPI.as_view(), name='disorder_api_list'),
    url(r'^task/json/(?P<uid>[\w\+%_& ]+)/$', graph.task_json, name="task_json"),
    url(r'^concept/json/(?P<uid>[\w\+%_& ]+)/$', graph.concept_json, name="concept_json"),
]

urlpatterns += api_urls
