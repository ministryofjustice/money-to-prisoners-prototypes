from django.shortcuts import render
from django.urls import path, include

urlpatterns = [
    path('', lambda request: render(request, 'index.html'), name='index'),
    path('noms_ops/', include('noms_ops.urls', 'noms_ops')),
]
