from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def check_and_set_last_title(context, title):
    if 'last_book_title' not in context or context['last_book_title'] != title:
        context['last_book_title'] = title
        return True
    return False

@register.simple_tag(takes_context=True)
def check_and_set_last_chapter(context, chapterName):
    if 'last_book_chapter' not in context or context['last_book_chapter'] != chapterName:
        context['last_book_chapter'] = chapterName
        return True
    return False

@register.simple_tag(takes_context=True)
def check_and_set_last_heading(context, headingName):
    if 'last_book_heading' not in context or context['last_book_heading'] != headingName:
        context['last_book_heading'] = headingName
        return True
    return False
