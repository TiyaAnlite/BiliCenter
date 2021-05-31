from . import common, bangumi
import bilibili_api


def path_all():
    path_modules = [
        common,
        bangumi
    ]
    for module in path_modules:
        for func in module.EXTEND_MODULE:
            setattr(getattr(bilibili_api, module.__name__.split(".")[-1]), func.__name__, func)
