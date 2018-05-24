from django.urls import path

from noms_ops.views import FilterView

app_name = 'noms_ops'
urlpatterns = [
    path('filters_1/', FilterView.as_view(prototype=1), name='filters_1'),
    path('filters_2/', FilterView.as_view(prototype=2), name='filters_2'),
]
