from django.urls import path

from noms_ops.views import CreditView, SenderView, PrisonerView

app_name = 'noms_ops'
urlpatterns = [
    path('filters/credits/', CreditView.as_view(), name='credits'),
    path('filters/senders/', SenderView.as_view(), name='senders'),
    path('filters/prisoners/', PrisonerView.as_view(), name='prisoners'),
]
