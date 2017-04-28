import json

from cognitiveatlas.api import get_task, get_concept, generate_url
from cognitiveatlas.utils import get_json
from jsoncompare import jsoncompare

base_ep = "http://192.168.99.100/api/"

def task_json_dump():
    all_tasks = []
    tasks = get_task().json
    for task in tasks:
        all_tasks.append(get_task(id=task['id']).json)
    with open("all_tasks.json", 'w') as fp:
        json.dump(all_tasks, fp)

def concept_json_dump():
    all_concepts = []
    concepts = get_concept().json
    for concept in concepts:
        all_concepts.append(get_concept(id=concept['id']).json)
    with open("all_concepts.json", 'w') as fp:
        json.dump(all_concepts, fp)

def compare_elems(file, url):
    missing_keys = {}
    all_mismatched_keys = {}

    with open(file, 'r') as fp:
        old_elems = json.load(fp)

    for old_elem in old_elems:
        new_elem = json.loads(get_json("{}?id={}".format(url, old_elem[0]['id'])))
        break
    '''
        mismatched_keys = []
        for elem in old_elem[0]:
            try:
                print(type(new_elem[str(elem)]))
                if type(old_elem[0][str(elem)]).__name__ == 'list':
                    for nested_elem in old_elem[0][str(elem)]:
                        if new_elem[str(elem)][nested_elem] != old_elem[0][str(elem)][nested_elem]:
                            mismatched_keys.append((str(new_elem[str(elem)][nested_elem]), str(old_elem[0][elem][nested_elem])))
                elif type(old_elem[0][str(elem)]).__name__ == 'str':
                    if new_elem[str(elem)] != old_elem[0][elem]:
                        mismatched_keys.append((str(new_elem[str(elem)]), str(old_elem[0][elem])))
            except KeyError as e:
                if missing_keys.get(e.args[0], None):
                    missing_keys[e.args[0]].append(new_elem['id'])
                else:
                    missing_keys[e.args[0]] = [new_elem['id']]
        if len(mismatched_keys) > 0:
            all_mismatched_keys[old_elem[0]['id']] = mismatched_keys
        break
    print(missing_keys.keys())

    with open("missmatched{}".format(file), 'w') as fp:
        json.dump(all_mismatched_keys, fp)
    '''


if  __name__ == '__main__':
    #task_json_dump()
    compare_elems("all_tasks.json", "{}{}".format(base_ep, "task"))

    #concept_json_dump()
    compare_elems("all_concepts.json", "{}{}".format(base_ep, "concept"))
