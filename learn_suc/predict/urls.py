from django.urls import path

from . import views

app_name = 'predict'
urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('', views.index, name='default'),
    path('index/', views.index, name='index'),
    path('type/summary/', views.type_summary, name='type_summary'),
    path('type/<int:type_id>/', views.type_detail, name='type_detail'),
    path('item/summary/', views.item_summary, name='item_summary'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('embedding/summary/', views.embedding_summary, name='embedding_summary'),
    path('embedding/<int:item_id>/', views.embedding_detail, name='embedding_detail'),
]
