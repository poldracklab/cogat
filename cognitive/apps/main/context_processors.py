from cognitive.apps.atlas.query import Concept, Task, Disorder, Theory, Battery

Concept = Concept()
Task = Task()
Disorder = Disorder()
Theory = Theory()
Battery = Battery()

# Needed on all pages
counts = {
    "disorders": Disorder.count(),
    "tasks": Task.count(),
    "concepts": Concept.count(),
    "collections": Battery.count() + Theory.count()
}

def counts_processor(request):
    return {'counts': counts}
