from django.urls import path

from . import views

app_name = 'predict'
urlpatterns = [
    # Test
    path('helloworld/', views.helloworld, name='helloworld'),
    # Debug
    path('item/summary/', views.item_summary, name='item_summary'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    # Default
    path('', views.index, name='default'),
    path('index/', views.index, name='index'),
    # Add, delete, suggest operations on item
    path('index/add_or_delete_items/', views.add_or_delete_items, name='add_or_delete_items'),
    path('index/search_item/', views.search_item, name='search_item'),
]
