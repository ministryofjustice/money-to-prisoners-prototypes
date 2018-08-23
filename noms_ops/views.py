from django.views.generic import FormView

from noms_ops.forms import CreditForm, SenderForm, PrisonerForm, DisbursementForm
from noms_ops.models import prisons, sources, methods, credit_statuses, disbursement_statuses


class FilterView(FormView):
    get = FormView.post
    form_valid = FormView.form_invalid

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET.dict()
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            object_list=context_data['form'].object_list,
            prisons=prisons,
            sources=sources,
            methods=methods,
            credit_statuses=credit_statuses,
            disbursement_statuses=disbursement_statuses,
        )
        return context_data


class CreditView(FilterView):
    title = 'Credits'
    template_name = 'noms_ops/credits.html'
    form_class = CreditForm


class SenderView(FilterView):
    title = 'Payment sources'
    template_name = 'noms_ops/senders.html'
    form_class = SenderForm


class PrisonerView(FilterView):
    title = 'Prisoners'
    template_name = 'noms_ops/prisoners.html'
    form_class = PrisonerForm
    axis = None


class DisbursementView(FilterView):
    title = 'Disbursements'
    template_name = 'noms_ops/disbursements.html'
    form_class = DisbursementForm
