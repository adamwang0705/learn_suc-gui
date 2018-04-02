from django.shortcuts import render
from django.http import HttpResponse

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
# LINE: Large-scale Information Network Embedding
# Behavior id: 347613
default_behavior = [2767459, 2906020, 2972072, 3078788, 3095165, 3169331, 3249647, 3255758, 3254437, 3263395, 1382595,
                    1492387, 1980713, 267563, 569799, 888462, 2127379, 882200, 1391569, 1605587, 178992, 641289,
                    1779357, 47992, 1986676, 1811546, 1353460]

default_rate = 90.0

def index(request):
    # Reset to default behavior
    request.session.setdefault('behavior', default_behavior)
    request.session.setdefault('rate', default_rate)

    behavior_info = []
    for item_id in request.session.get('behavior'):
        item = Item.objects.get(pk=item_id)
        behavior_info.append({'name': item.name, 'type': item.type.name})

    authors = Item.objects.filter(type__name='author').order_by('name')[:20]
    context = {'displaying_type': 'author',
               'displaying_items': authors,
               'behavior_info': behavior_info,
               'rate': request.session.get('rate')}
    return render(request, 'predict/compose_behavior.html', context)
