from django.views.generic import FormView

from noms_ops.forms import FilterForm
from noms_ops.models import prisons, sources, statuses


class FilterView(FormView):
    template_name = 'noms_ops/filters.html'
    form_class = FilterForm

    get = FormView.post
    form_valid = FormView.form_invalid

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET.dict()
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            credits_list=context_data['form'].credits_list,
            prisons=prisons,
            sources=sources,
            statuses=statuses,
        )
        return context_data
