from django.shortcuts import render

from cognitive.apps.atlas.query import Concept, Task, Disorder, Theory, Battery
from cognitive.settings import DOMAIN

Concept = Concept()
Task = Task()
Disorder = Disorder()
Theory = Theory()
Battery = Battery()


def base(request):

    # We only need id and name for the home page
    fields = ["id", "name"]

    concepts = Concept.all(limit=10, order_by="last_updated", fields=fields)
    tasks = Task.all(limit=10, order_by="last_updated", fields=fields)
    disorders = Disorder.all(limit=10, order_by="last_updated", fields=fields)
    theories = Theory.all(limit=7, order_by="last_updated", fields=fields)

    appname = "The Cognitive Atlas"
    context = {'appname': appname,
               'active': 'homepage',
               'concepts': concepts,
               'tasks': tasks,
               'theories': theories,
               'disorders': disorders, }

    return context


def index(request):
    context = base(request)
    return render(request, 'main/index.html', context)


def about(request):
    context = base(request)
    return render(request, 'main/about.html', context)


def api(request):
    context = base(request)
    context["domain"] = DOMAIN
    return render(request, 'main/api.html', context)
