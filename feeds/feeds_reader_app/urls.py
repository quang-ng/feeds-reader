from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:channel_id>/', views.detail_channel, name='detail'),
    path('edit_channel/<int:channel_id>/', views.edit_channel, name='edit'),
    path('new_channel/', views.edit_channel, name='new_channel'),
    path('delete_channel/<int:channel_id>/', views.delete_channel, name='edit'),
    path('items/<int:channel_id>/', views.items, name='edit'),
    path('detail_item/<int:item_id>/', views.detail_item, name='edit'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit'),
    path('new_item/<int:channel_id>/', views.edit_item, name='edititem'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
]