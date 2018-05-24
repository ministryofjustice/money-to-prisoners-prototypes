import itertools
import json
from urllib.parse import urlencode

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def dump_credit(credit):
    return mark_safe(json.dumps(credit, cls=DjangoJSONEncoder))


@register.filter
def currency(pence_value):
    try:
        return '£{:,.2f}'.format(pence_value / 100)
    except TypeError:
        return pence_value


@register.simple_tag
def format_choice(choices, key):
    return choices.get(key, key)


@register.simple_tag
def section_selected(form, key):
    return form.is_section_selected(key)


@register.simple_tag
def hidden_fields_excluding_section(form, key):
    data = form.get_query_data()
    included = itertools.chain.from_iterable(form.sections[section] for section in form.sections if section != key)
    excluded = set(data.keys()) - set(included) - {'ordering'}
    return format_html_join(
        '\n',
        '<input type="hidden" name="{}" value="{}" />',
        ((name, value) for name, value in data.items() if name not in excluded)
    )


@register.filter
def ordering_classes(form, ordering):
    current_ordering = form.cleaned_data.get('ordering')
    if current_ordering == ordering:
        return 'results-ordering--asc'
    if current_ordering == '-%s' % ordering:
        return 'results-ordering--desc'
    return ''


@register.filter
def query_string_with_reversed_ordering(form, ordering):
    data = form.get_query_data()
    current_ordering = data.get('ordering')
    if current_ordering == ordering:
        ordering = '-%s' % ordering
    data['ordering'] = ordering
    return urlencode(data, doseq=True)
