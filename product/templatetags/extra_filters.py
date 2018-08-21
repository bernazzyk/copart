from django import template

register = template.Library()


@register.filter
def get_by_index(l, i):
    return l[i]
