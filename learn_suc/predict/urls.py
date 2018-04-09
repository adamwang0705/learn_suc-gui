from django.urls import path

from . import views

app_name = 'predict'
urlpatterns = [
    # Test
    path('helloworld/', views.helloworld, name='helloworld'),
    # Debug
    path('type/summary/', views.type_summary, name='type_summary'),
    path('type/<int:type_id>/', views.type_detail, name='type_detail'),
    path('item/summary/', views.item_summary, name='item_summary'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('embedding/summary/', views.embedding_summary, name='embedding_summary'),
    path('embedding/<int:item_id>/', views.embedding_detail, name='embedding_detail'),
    # Default
    path('', views.index, name='default'),
    path('index/', views.index, name='index'),
    # Delete selected item
    path('index/delete_item/', views.delete_item, name='delete_item'),
    path('index/add_item/', views.add_item, name='add_item'),
    # TODO: suggest item
]
