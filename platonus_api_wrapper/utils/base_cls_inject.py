from functools import wraps


def inheritance_from_base_cls(method):
    @wraps(method)
    def base_cls_inject(self, *args, **kwargs):
        return method(self.base_cls, *args, **kwargs)

    return base_cls_inject
