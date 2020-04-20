from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    if not isinstance(dictionary, dict):
        return ""
    res = dictionary.get(key)
    if not res:
        return ""
    else:
        return res