from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:channel_id>/', views.detail_channel, name='detail'),
    path('edit_channel/<int:channel_id>/', views.edit_channel, name='edit')
]