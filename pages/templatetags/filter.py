from django.template.defaulttags import register


@register.filter
def is_true(dictionary, key):
    res = dictionary.get(key)
    if not res:
        return False
    else:
        return res[0] == 'true' or res == 'true'


@register.filter
def get_first_item(dictionary, key):
    res = dictionary.get(key)
    if not res:
        return ""
    else:
        return res[0]


@register.filter
def s_format(string, f):
    return string.format(f)


@register.filter
def split(str, spliter=None):
    if not spliter:
        return str.split()
    return str.split(spliter)


@register.filter
def clear(str):
    return str.replace("&#39;", "")