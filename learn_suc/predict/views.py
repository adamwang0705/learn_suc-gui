from django.shortcuts import render
from django.http import HttpResponse

from .models import Type, Item, Embedding

# Create your views here.

"""
For debug
"""
def helloworld(request):
    return HttpResponse('Hello World. LearnSUC online powered by Django.')


def type_list(request):
    types = Type.objects.all()
    context = {'types': types}
    return render(request, 'predict/types.html', context)


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
Public interface
"""
# def index(request):
#     authors = Item.objects.filter(type__name='author')[:500]

