from django.shortcuts import render
from django.http import HttpResponse

import os
import numpy as np
from sklearn.externals import joblib

from .models import Type, Item, Embedding

# Create your views here.

"""For debug"""
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


"""Public interface"""
lr_model_file = os.path.join('.', 'learn_suc-m2-d64-n10.model.pkl')
lr_model = joblib.load(lr_model_file)

def predict_success_rate(behavior):
    # Compute behavior vector
    behavior_vec = []
    for item_id in behavior:
        embedding = Embedding.objects.get(pk=item_id).embedding
        item_vec = [float(dim) for dim in embedding.split()]
        behavior_vec.append(item_vec)
    behavior_vec = np.sum(behavior_vec, axis=0)

    # Compute prediction
    success_rate = lr_model.predict_proba(behavior_vec.reshape(1, -1))[0][1]
    return success_rate*100


# LINE: Large-scale Information Network Embedding
# Behavior id: 347613
default_behavior = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395, 1382595,
                    1492387, 1980713, 267563, 569799, 888462, 2127379, 882200, 1391569, 1605587, 178992, 641289,
                    1779357, 47992, 1986676, 1811546, 1353460]

# default_behavior = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395, 1382595,
#                     1492387, 1980713, 267563, 569799]

default_rate = predict_success_rate(default_behavior)

def index(request):
    # Reset to default behavior
    # request.session.setdefault('curr_behavior', default_behavior)
    # request.session.setdefault('curr_rate', default_rate)
    request.session['curr_behavior'] = default_behavior
    request.session['curr_rate'] = default_rate

    curr_behavior_info = []
    for item_id in request.session.get('curr_behavior'):
        item = Item.objects.get(pk=item_id)
        curr_behavior_info.append({'item_id': item_id, 'name': item.name, 'type': item.type.name})

    displaying_type = 'author'
    displaying_items = Item.objects.filter(type__name=displaying_type).order_by('name')[:50]
    context = {'displaying_type': displaying_type,
               'displaying_items': displaying_items,
               'curr_behavior_info': curr_behavior_info,
               'curr_rate': request.session.get('curr_rate')}
    return render(request, 'predict/compose_behavior.html', context)


def delete_item(request):
    # Receive delete items
    delete_items = request.POST.getlist('m_select_delete_item')

    # Compute current behavior and current rate
    curr_behavior = request.session.get('curr_behavior')
    for item in delete_items:  # keep the original items order
        curr_behavior.remove(int(item))
    curr_rate = predict_success_rate(curr_behavior)

    # Update session variables
    request.session['curr_behavior'] = curr_behavior
    request.session['curr_rate'] = curr_rate

    # Update context variables
    curr_behavior_info = []
    for item_id in request.session.get('curr_behavior'):
        item = Item.objects.get(pk=item_id)
        curr_behavior_info.append({'item_id': item_id, 'name': item.name, 'type': item.type.name})

    context = {'curr_behavior_info': curr_behavior_info,
               'curr_rate': request.session.get('curr_rate')}
    return render(request, 'predict/compose_behavior.html', context)
