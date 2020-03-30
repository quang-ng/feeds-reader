from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:channel_id>/', views.detail_channel, name='detail'),
    path('edit_channel/<int:channel_id>/', views.edit_channel, name='edit'),
    path('items/<int:channel_id>/', views.items, name='edit'),
    path('detail_item/<int:item_id>/', views.detail_item, name='edit'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit'),
]