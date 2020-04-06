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


@register.filter
def remove_lang(s):
    urls = s.split('/')
    res = ''
    for i in range(2, len(urls)):
        res += '/' + urls[i]
    return res


@register.filter
def get_lang(s):
    return s.split('/')[1]