def get_pre_url(request):
    try:
        next = request.META.get('HTTP_REFERER')
        return next
    except:
        return '/'

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value