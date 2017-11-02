from cognitive.apps.atlas import query

Concept = query.Concept()
Task = query.Task()
Disorder = query.Disorder()
Theory = query.Theory()
Battery = query.Battery()
Behavior = query.Behavior()
Trait = query.Trait()

# Needed on all pages
counts = {
    "disorders": Disorder.count(),
    "tasks": Task.count(),
    "concepts": Concept.count(),
    "collections": Battery.count() + Theory.count(),
    "phenotypes": (Disorder.count() + Trait.count() + Behavior.count()),
}

def counts_processor(request):
    return {'counts': counts}
