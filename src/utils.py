from functools import wraps


def listify(fn=None, wrapper=list):
    """
    A decorator which wraps a function's return value in ``list(...)``.

    Useful when an algorithm can be expressed more cleanly as a generator but
    the function should return a list.
    :param fn:
    :param wrapper:

    Example::

        >>> @listify
        ... def get_lengths(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths(["spam", "eggs"])
        [4, 4]
        >>>
        >>> @listify(wrapper=tuple)
        ... def get_lengths_tuple(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths_tuple(["foo", "bar"])
        (3, 3)
    """

    def listify_return(fn):
        @wraps(fn)
        def listify_helper(*args, **kw):
            return wrapper(fn(*args, **kw))

        return listify_helper

    if fn is None:
        return listify_return
    return listify_return(fn)

UTF8 = 'utf8'
CP1252 = 'cp1252'
UTF16 = 'utf16'
ENCODINGS = (UTF8, CP1252, UTF16)


def read_text_file(p):
    with open(p, 'rt') as f:
        return f.read()


def write_text_file(f_name, content, encoding=None, lines=False):
    with open(f_name, 'wt', encoding=encoding or UTF8) as f:
        if lines:
            f.writelines(content)
        else:
            f.write(content)
    return f_name

