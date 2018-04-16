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
    # Add, delete, suggest operations on item
    path('index/delete_multiple_items/', views.delete_multiple_items, name='delete_multiple_items'),
    path('index/add_multiple_items/', views.add_multiple_items, name='add_multiple_items'),
    path('index/suggest_item/', views.suggest_item, name='suggest_item'),
    path('index/add_suggested_item/', views.add_suggested_item, name='add_suggested_item'),
]
