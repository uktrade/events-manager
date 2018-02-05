from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authorised', views.authorised, name='authorised'),
    path('accounts/login/', views.login_via_sso_provider, name='login_via_sso_provider'),
]
