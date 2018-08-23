from django.urls import path

from noms_ops.views import CreditView, SenderView, PrisonerView, DisbursementView

app_name = 'noms_ops'
urlpatterns = [
    path('credits/', CreditView.as_view(), name='credits'),
    path('credits/senders/', SenderView.as_view(), name='senders'),
    path('credits/prisoners/', PrisonerView.as_view(axis='credits'), name='prisoners'),

    path('disbursements/', DisbursementView.as_view(), name='disbursements'),
    path('disbursements/prisoners/', PrisonerView.as_view(axis='disbursements'), name='prisoners-disbursements'),
]
