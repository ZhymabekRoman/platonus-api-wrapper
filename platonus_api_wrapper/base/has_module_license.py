from ..utils.base_cls_inject import inheritance_from_base_cls
from ..utils.loginizer import login_required
from ..utils.lru_cacher import timed_lru_cache


class HasModuleLicense:
    def __init__(self, base_cls):
        self.base_cls = base_cls

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def technical_support(self):
        response = self.session.get(
            self.api.has_module_license("technical_support")
        ).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def online_consultant(self):
        response = self.session.get(
            self.api.has_module_license("online_consultant")
        ).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def extended_license(self):
        response = self.session.get(
            self.api.has_module_license("extended_license")
        ).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def profile(self):
        response = self.session.get(self.api.has_module_license("profile")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def for_visually_impaired(self):
        response = self.session.get(
            self.api.has_module_license("for_visually_impaired")
        ).as_object()
        return response
