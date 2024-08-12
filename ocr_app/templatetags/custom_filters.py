from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def highlight(text, search):
    if search:
        regex = re.compile(re.escape(search), re.IGNORECASE)
        highlighted = regex.sub(lambda match: f'<span class="highlight">{match.group(0)}</span>', text)
        return mark_safe(highlighted)
    return text