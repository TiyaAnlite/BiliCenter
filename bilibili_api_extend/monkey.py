from . import utils, common, bangumi
import bilibili_api


def path_headers():
    bilibili_api.utils.DEFAULT_HEADERS = utils.DEFAULT_HEADERS


def path_all():
    path_headers()
    path_modules = [
        common,
        bangumi
    ]
    for module in path_modules:
        for func in module.EXTEND_MODULE:
            setattr(getattr(bilibili_api, module.__name__.split(".")[-1]), func.__name__, func)
