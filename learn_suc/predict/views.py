import os
import json
from string import ascii_lowercase
from collections import OrderedDict
import numpy as np
from sklearn.externals import joblib

from django.shortcuts import render
from django.http import HttpResponse
from .models import Item
from django.conf import settings
from django.core.cache import caches

# Create your views here.

"""
Debug only
"""
def helloworld(request):
    return HttpResponse('Hello World. LearnSUC online powered by Django.')


def item_summary(request):
    item_num = Item.objects.count()
    author_num = Item.objects.filter(type=0).count()
    conference_num = Item.objects.filter(type=1).count()
    keyword_num = Item.objects.filter(type=2).count()
    reference_num = Item.objects.filter(type=3).count()
    return HttpResponse('{} items in db. -authors: {}; -conference: {}; -keyword: {}; -reference: {};'
                        .format(item_num, author_num, conference_num, keyword_num, reference_num))


def item_detail(request, item_id):
    item = Item.objects.get(pk=item_id)
    return HttpResponse('Item {}: -name: {}; -type: {}; -embedding: {}'
                        .format(item_id, item.name, item.type, item.embedding))


"""
Preparations
"""
''' Type and type_name mappings '''
type_names_ = ['author', 'conference', 'keyword', 'reference']
type_name2type = {'author': 0, 'conference': 1, 'keyword': 2, 'reference': 3}

''' LR model '''
lr_model_file = os.path.join(settings.BASE_DIR, 'learn_suc-m2-d64-n10.model.pkl')
lr_model = joblib.load(lr_model_file)

''' Cache objs for selected items and displaying items '''
selected_items_cache = caches['selected_items_cache']
displaying_items_cache = caches['displaying_items_cache']


def _get_selected_items_in_cache_or_query(item_ids_):
    """
    Get item from cache. Or, look up in database.
    :param item_ids_: List of item ids
    :return:
    """
    items = OrderedDict()
    for item_id in item_ids_:
        # If item not found in cache
        if item_id not in selected_items_cache:
            # Query item from db
            item_obj = Item.objects.get(pk=item_id)
            item_dic = {'name': item_obj.name,
                        'type': item_obj.type,
                        'embedding': [float(e) for e in item_obj.embedding.split(' ')]}
            # Update cache
            selected_items_cache.add(item_id, item_dic)
            # Add to result
            items[item_id] = item_dic
        # Item already exits in cache
        else:
            items[item_id] = selected_items_cache.get(item_id)
    return items

def _predict_success_rate(item_embeddings_):
    """
    Compute success rate by using LR model based on list of item embeddings
    :param item_embeddings_:
    :return:
    """
    if item_embeddings_:
        # Compute behavior vector
        behavior_vec = np.sum(item_embeddings_, axis=0)
        # Compute prediction
        success_rate = lr_model.predict_proba(behavior_vec.reshape(1, -1))[0][1]
        return success_rate * 100
    else:
        return 0


''' Default selected item ids '''
# LINE: Large-scale Information Network Embedding (id: 347613)
# default_behavior_items_ = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395,
#                            1382595, 1492387, 1980713, 267563, 569799, 888462, 2127379, 882200, 1391569, 1605587,
#                            178992, 641289, 1779357, 47992, 1986676, 1811546, 1353460]

default_selected_item_ids_ = [2767459, 2906020, 2972072, 3078788, 3249647, 3255758, 3254437, 3263395,
                              1382595, 1492387, 1980713, 267563, 569799, 888462, 2127379, 1391569, 1605587,
                              178992, 641289, 1779357, 47992, 1986676, 1811546, 1353460]

default_selected_items = _get_selected_items_in_cache_or_query(default_selected_item_ids_)
default_success_rate = _predict_success_rate([default_selected_items[item_id]['embedding']
                                              for item_id in default_selected_items.keys()])

''' Default display item filters '''
default_displaying_type_name = type_names_[0]
all_fls_ = list(ascii_lowercase)
default_displaying_fl = all_fls_[0]


"""
Public interface
"""
def index(request):
    displaying_type_name = request.GET.get('filter_type_select', default_displaying_type_name)
    displaying_fl = request.GET.get('filter_fl_select', default_displaying_fl)

    # Initialize default session variables
    request.session['displaying_type_name'] = displaying_type_name
    request.session['displaying_fl'] = displaying_fl

    if not request.session.get('selected_item_ids', None):
        request.session['selected_item_ids'] = default_selected_item_ids_

    # Build context dict variable for selected items from cache
    selected_items = _get_selected_items_in_cache_or_query(request.session['selected_item_ids'])
    selected_items_info = []
    for item_id in selected_items.keys():
        selected_items_info.append({'item_id': item_id,
                                    'name': selected_items[item_id]['name'],
                                    'type_name': type_names_[selected_items[item_id]['type']]})

    # Compute success for selected items
    success_rate = _predict_success_rate([selected_items[item_id]['embedding']
                                          for item_id in selected_items.keys()])

    # Build context dict variable for displaying items by querying db
    # Also, cache current batch of displaying items info
    displaying_items = Item.objects.filter(type=type_name2type[request.session.get('displaying_type_name')],
                                           name_fl=request.session['displaying_fl']).order_by('name')[:200]
    displaying_items_info = []
    for item in displaying_items:
        displaying_items_info.append({'item_id': item.id,
                                      'name': item.name,
                                      'type_name': type_names_[item.type]})
    displaying_items_cache.add('latest_displaying_items_info', displaying_items_info)

    context = {'selected_items_info': selected_items_info,
               'selected_success_rate': success_rate,
               'displaying_items_info': displaying_items_info,
               'type_names': type_names_,
               'displaying_type_name': request.session.get('displaying_type_name'),
               'filter_fls': all_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)


def add_or_delete_items(request):
    """
    Deal with POST requests from delete_items_form, add_items_form and search_item_form in template.
    :param request:
    :return:
    """
    # Get last step selected item ids
    selected_item_ids = request.session.get('selected_item_ids')

    # Update selected item ids list
    if request.POST.getlist('add_items_multiple_select'):  # Handle add_items_form
        # Receive add items
        added_items = request.POST.getlist('add_items_multiple_select')
        # Add into selected items
        for item_id_str in added_items:  # keep the original items order
            if int(item_id_str) not in selected_item_ids:
                selected_item_ids.append(int(item_id_str))
    elif request.POST.getlist('delete_items_multiple_select'):   # Handle delete_items_form
        # Receive delete items
        deleted_items = request.POST.getlist('delete_items_multiple_select')
        # Remove from selected items and compute new success rate
        for item_id_str in deleted_items:  # keep the original items order
            selected_item_ids.remove(int(item_id_str))
    elif request.POST.get('searched_item_id'):   # Handle search_item_form
        # Receive add item
        added_item = request.POST.get('searched_item_id')
        # Add into selected items
        if int(added_item) not in selected_item_ids:
            selected_item_ids.append(int(added_item))
    else:
        pass

    # Update session variables
    request.session['selected_item_ids'] = selected_item_ids

    # Build context dict variable for selected items from cache
    selected_items_info = []
    selected_items = _get_selected_items_in_cache_or_query(selected_item_ids)
    for item_id in selected_items.keys():
        selected_items_info.append({'item_id': item_id,
                                    'name': selected_items[item_id]['name'],
                                    'type_name': type_names_[selected_items[item_id]['type']]})

    new_success_rate = _predict_success_rate([selected_items[item_id]['embedding']
                                              for item_id in selected_items.keys()])

    # Retrieve context dict variable for displaying items from cache
    displaying_items_info = displaying_items_cache.get('latest_displaying_items_info')

    context = {'selected_items_info': selected_items_info,
               'selected_success_rate': new_success_rate,
               'displaying_items_info': displaying_items_info,
               'type_names': type_names_,
               'displaying_type_name': request.session.get('displaying_type_name'),
               'filter_fls': all_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)


def search_item(request, len_limit=100):
    """
    Deal with AJAX request from search_item_form in template.
    :param request:
    :param len_limit:
    :return:
    """
    if request.is_ajax():
        query = request.GET.get('term', '')

        displaying_type_name = request.session.get('displaying_type_name')
        autocomplete_items = Item.objects.filter(type=type_name2type[displaying_type_name],
                                                 name__icontains=query).order_by('name')[:len_limit]

        results = []
        for item in autocomplete_items:
            if item.type in [0, 4]:
                _formatted_item_name = item.name.title()
            elif item.type == 1:
                _formatted_item_name = item.name.upper()
            else:
                _formatted_item_name = item.name.lower()
            item_json = {'item_id': item.id, 'name': _formatted_item_name, 'type_name': type_names_[item.type]}
            results.append(item_json)
        data = json.dumps(results)
    else:
        data = 'empty'
    return HttpResponse(data, content_type="application/json")
