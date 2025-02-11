from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_pays, name='liste'),
    path('afficher/', views.afficher_pays, name='afficher'),
]
