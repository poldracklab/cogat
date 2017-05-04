''' functions to help with comparing the old cognitive atlas api with
    the new one '''
import json

from cognitiveatlas.api import get_task, get_concept, get_disorder
from cognitiveatlas.utils import get_json

BASE_EP = "http://192.168.99.100/api/"

def task_json_dump():
    ''' use cognitiveatlas library to dump tasks to a json file '''
    all_tasks = []
    tasks = get_task().json
    for task in tasks:
        all_tasks.append(get_task(id=task['id']).json)
    with open("all_tasks.json", 'w') as fp:
        json.dump(all_tasks, fp)

def concept_json_dump():
    ''' use cognitiveatlas library to dump concepts to a json file '''
    all_concepts = []
    concepts = get_concept().json
    for concept in concepts:
        all_concepts.append(get_concept(id=concept['id']).json)
    with open("all_concepts.json", 'w') as fp:
        json.dump(all_concepts, fp)

def disorder_json_dump():
    ''' use cognitiveatlas library to dump disorders to a json file '''
    all_disorders = []
    disorders = get_disorder().json
    for disorder in disorders:
        all_disorders.append(get_disorder(id=disorder['id']).json)
    with open("all_disorders.json", 'w') as fp:
        json.dump(all_disorders, fp)

def dict_in_list(old_dict, new_list):
    ''' See if a given dictionary from the old api appears in a list of
        dictionaries from the new api.'''
    for new_dict in new_list:
        compare_dicts(old_dict, new_dict)

def compare_dicts(old_dict, new_dict, ignore_keys=[]):
    ''' iterate over the keys of the old api dictionary and compare_values
        with the new dict. If the key is missing add an entry to a dictionary
        with the old dict key as the key, and append the id of the new api
        object missing the key as/to the value'''
    missing_keys = {}
    mismatched_value = []
    mismatched_types = []
    old_dict = old_dict
    for old_key in old_dict:
        if old_key in ignore_keys:
            continue
        try:
            old_value = old_dict[old_key]
            new_value = new_dict[old_key]
            if type(old_value).__name__ == 'list' and type(new_value).__name__ == 'list':
                if len(old_value) != len(new_value):
                    mismatched_value.append((old_dict['id'], old_key, len(old_value), len(new_value)))
            elif type(old_value).__name__ == 'str' and type(new_value).__name__ == 'str':
                if old_value != new_value:
                    mismatched_value.append((old_dict['id'], old_key, old_value, new_value))
            else:
                mismatched_types.append((old_dict['id'], old_key, old_value, new_value))
        except KeyError as error:
            if missing_keys.get(error.args[0], None):
                missing_keys[error.args[0]].append(new_dict['id'])
            else:
                missing_keys[error.args[0]] = [new_dict['id']]
    if missing_keys:
        print(missing_keys)
    if mismatched_value:
        print(mismatched_value)
    if mismatched_types:
        print(mismatched_types)

def compare_api_elems(file, url, ignore_keys=[]):
    ''' iterate over a  json file and attempt to lookup each element at
        a remote url and see what differences there are between the two
        elements'''
    with open(file, 'r') as fp:
        old_elems = json.load(fp)

    for old_elem in old_elems:
        new_elem = json.loads(get_json("{}?id={}".format(url, old_elem[0]['id'])))
        compare_dicts(old_elem[0], new_elem, ignore_keys)

if  __name__ == '__main__':
    #task_json_dump()
    #ignore_keys = ['concept_class', 'umark', 'umarkdef', 'conclass', 'event_stamp', 'def_event_stamp', 'discussion', 'history']
    #compare_api_elems("all_tasks.json", "{}{}".format(BASE_EP, "task"), ignore_keys)

    #concept_json_dump()
    #ignore_keys = ['concept_class', 'def_event_stamp', 'event_stamp', 'definition_text']
    #compare_api_elems("all_concepts.json", "{}{}".format(BASE_EP, "concept"), ignore_keys)

    #disorder_json_dump()
    ignore_keys = ['tid', 'type']
    compare_api_elems("all_disorders.json", "{}{}".format(BASE_EP, "disorder"))
