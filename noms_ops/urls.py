from django.urls import path

from noms_ops.views import FilterView

app_name = 'noms_ops'
urlpatterns = [
    path('filters/', FilterView.as_view(), name='filters'),
]
