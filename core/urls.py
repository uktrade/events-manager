from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authorised', views.when_authorised_from_sso_provider, name='authorised'),
    path('logout', views.logout, name='logout'),
]
