from django import template
import re

register = template.Library()

@register.filter
def add_str(value, arg):
    return str(value) + str(arg)

@register.filter
def reg(value, arg):
    return re.search(arg,value).group(1)