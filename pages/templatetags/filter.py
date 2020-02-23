from django.template.defaulttags import register


@register.filter
def get(dictionary, key):
    return dictionary.get(key)


@register.filter
def format(string, f):
    return string.format(f)


@register.filter
def split(s, spliter=None):
    if not spliter:
        return s.split()
    return s.split(spliter)
