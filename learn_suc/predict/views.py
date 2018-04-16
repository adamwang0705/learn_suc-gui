from django.shortcuts import render, redirect
from django.http import HttpResponse

import os
import json
from string import ascii_lowercase
import numpy as np
from sklearn.externals import joblib

from .models import Type, Item, Embedding

# Create your views here.
"""
Debug only
"""


def helloworld(request):
    return HttpResponse('Hello World. LearnSUC online powered by Django.')


def type_summary(request):
    type_num = Type.objects.count()
    return HttpResponse('{} types in db.'.format(type_num))


def type_detail(request, type_id):
    itype = Type.objects.get(pk=type_id)
    return HttpResponse('Type {}: -name: {};'.format(type_id, itype.name))


def item_summary(request):
    item_num = Item.objects.count()
    author_num = Item.objects.filter(type__name='author').count()
    conference_num = Item.objects.filter(type__name='conference').count()
    keyword_num = Item.objects.filter(type__name='keyword').count()
    reference_num = Item.objects.filter(type__name='reference').count()
    return HttpResponse('{} items in db. -authors: {}; -conference: {}; -keyword: {}; -reference: {};'
                        .format(item_num, author_num, conference_num, keyword_num, reference_num))


def item_detail(request, item_id):
    item = Item.objects.get(pk=item_id)
    return HttpResponse('Item {}: -name: {}; -notes: {};'.format(item_id, item.name, item.notes))


def embedding_summary(request):
    embedding_num = Embedding.objects.count()
    return HttpResponse('{} embeddings in db.'.format(embedding_num))


def embedding_detail(request, item_id):
    embedding = Embedding.objects.get(pk=item_id)
    return HttpResponse('Item {}: -embedding: {};'.format(item_id, embedding.embedding))


"""
LR model, success rate function, and default behavior
"""
lr_model_file = os.path.join('.', 'learn_suc-m2-d64-n10.model.pkl')
lr_model = joblib.load(lr_model_file)


def _predict_success_rate(items):
    if items:
        # Compute behavior vector
        behavior_vec = []
        for item_id in items:
            embedding_str = Embedding.objects.get(pk=item_id).embedding
            item_vec = [float(dim) for dim in embedding_str.split()]
            behavior_vec.append(item_vec)
        behavior_vec = np.sum(behavior_vec, axis=0)

        # Compute prediction
        success_rate = lr_model.predict_proba(behavior_vec.reshape(1, -1))[0][1]
        return success_rate * 100
    else:
        return 0


# LINE: Large-scale Information Network Embedding
# Behavior id: 347613
default_behavior_items_ = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395,
                           1382595, 1492387, 1980713, 267563, 569799, 888462, 2127379, 882200, 1391569, 1605587,
                           178992, 641289, 1779357, 47992, 1986676, 1811546, 1353460]

# default_behavior = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395, 1382595,
#                     1492387, 1980713, 267563, 569799]

default_success_rate = _predict_success_rate(default_behavior_items_)
default_displaying_type = 'author'
default_fls_ = list(ascii_lowercase)


def _retrieve_items_info(selected_items, len_limit=1000):
    items_info = []
    if len(selected_items) > len_limit:
        selected_items = selected_items[:len_limit]
    for item_id in selected_items:
        item = Item.objects.get(pk=item_id)
        items_info.append({'item_id': item_id, 'name': item.name, 'type_name': item.type.name})
    return items_info


"""
Public interface
"""


def index(request):
    displaying_type = request.GET.get('filter_type_select', default_displaying_type)
    displaying_fl = request.GET.get('filter_fl_select', default_fls_[0])
    request.session['displaying_type'] = displaying_type
    request.session['displaying_fl'] = displaying_fl

    # Assign default behavior items
    if not request.session.get('selected_items', None):
        request.session['selected_items'] = default_behavior_items_
    if not request.session.get('selected_success_rate', None):
        request.session['selected_success_rate'] = default_success_rate
    if not request.session.get('type_names', None):
        request.session['type_names'] = list(Type.objects.all().order_by('id').values_list('name', flat=True))

    # Build context dict variable
    displaying_items = Item.objects.filter(type__name=request.session.get('displaying_type'),
                                           name__startswith=request.session['displaying_fl'])\
        .order_by('name').values_list('id', flat=True)

    context = {'selected_items_info': _retrieve_items_info(request.session.get('selected_items')),
               'selected_success_rate': request.session.get('selected_success_rate'),
               'displaying_type': request.session.get('displaying_type'),
               'displaying_items_info': _retrieve_items_info(displaying_items),
               'type_names': request.session['type_names'],
               'filter_fls': default_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)


def delete_multiple_items(request):
    # Receive delete items
    delete_items = request.POST.getlist('delete_item_multiple_select')

    # Remove from selected items and compute new success rate
    selected_items = request.session.get('selected_items')
    for item_id_str in delete_items:  # keep the original items order
        selected_items.remove(int(item_id_str))
    selected_success_rate = _predict_success_rate(selected_items)

    # Update session variables
    request.session['selected_items'] = selected_items
    request.session['selected_success_rate'] = selected_success_rate

    # Build context dict variable
    displaying_items = Item.objects.filter(type__name=request.session.get('displaying_type'),
                                           name__startswith=request.session['displaying_fl'])\
        .order_by('name').values_list('id', flat=True)
    context = {'selected_items_info': _retrieve_items_info(request.session.get('selected_items')),
               'selected_success_rate': request.session.get('selected_success_rate'),
               'displaying_type': request.session.get('displaying_type'),
               'displaying_items_info': _retrieve_items_info(displaying_items),
               'type_names': request.session['type_names'],
               'filter_fls': default_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)


def add_multiple_items(request):
    # Receive add items
    add_items = request.POST.getlist('add_item_multiple_select')

    # Add into selected items and compute new success rate
    selected_items = request.session.get('selected_items')
    for item_id_str in add_items:  # keep the original items order
        if int(item_id_str) not in selected_items:
            selected_items.append(int(item_id_str))
    selected_success_rate = _predict_success_rate(selected_items)

    # Update session variables
    request.session['selected_items'] = selected_items
    request.session['selected_success_rate'] = selected_success_rate

    # Build context dict variable
    displaying_items = Item.objects.filter(type__name=request.session.get('displaying_type'),
                                           name__startswith=request.session['displaying_fl'])\
        .order_by('name').values_list('id', flat=True)

    context = {'selected_items_info': _retrieve_items_info(request.session.get('selected_items')),
               'selected_success_rate': request.session.get('selected_success_rate'),
               'displaying_type': request.session.get('displaying_type'),
               'displaying_items_info': _retrieve_items_info(displaying_items),
               'type_names': request.session['type_names'],
               'filter_fls': default_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)


def suggest_item(request, len_limit=200):
    if request.is_ajax():
        query = request.GET.get('term', '')

        displaying_type = request.session.get('displaying_type')

        suggested_items = Item.objects.filter(type__name=displaying_type, name__icontains=query).order_by('name')
        results = []
        if suggested_items.count() > len_limit:
            suggested_items = suggested_items[:200]
        for item in suggested_items:
            item_json = {'item_id': item.id, 'name': item.name, 'type_name': item.type.name}
            results.append(item_json)
        data = json.dumps(results)
    else:
        data = 'empty'
    return HttpResponse(data, content_type="application/json")


def add_suggested_item(request):
    # Receive add item
    add_item = request.POST.get('suggested_item_id')
    print('*** {}'.format(add_item))

    # Add into selected items and compute new success rate
    selected_items = request.session.get('selected_items')

    if int(add_item) not in selected_items:
        selected_items.append(int(add_item))
    selected_success_rate = _predict_success_rate(selected_items)

    # Update session variables
    request.session['selected_items'] = selected_items
    request.session['selected_success_rate'] = selected_success_rate

    # Build context dict variable
    displaying_items = Item.objects.filter(type__name=request.session.get('displaying_type'),
                                           name__startswith=request.session['displaying_fl'])\
        .order_by('name').values_list('id', flat=True)
    context = {'selected_items_info': _retrieve_items_info(request.session.get('selected_items')),
               'selected_success_rate': request.session.get('selected_success_rate'),
               'displaying_type': request.session.get('displaying_type'),
               'displaying_items_info': _retrieve_items_info(displaying_items),
               'type_names': request.session['type_names'],
               'filter_fls': default_fls_,
               'displaying_fl': request.session['displaying_fl']}
    return render(request, 'predict/prediction.html', context)
