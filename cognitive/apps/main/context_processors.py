def counts_processor(request):
    import cognitive.apps.atlas.query as query

    Concept = query.Concept()
    Task = query.Task()
    Disorder = query.Disorder()
    Theory = query.Theory()
    Battery = query.Battery()
    Behavior = query.Behavior()
    Trait = query.Trait()

    counts = {
        "disorders": Disorder.count(),
        "tasks": Task.count(),
        "concepts": Concept.count(),
        "collections": Battery.count() + Theory.count(),
        "phenotypes": (Disorder.count() + Trait.count() + Behavior.count()),
    }

    return {'counts': counts}
