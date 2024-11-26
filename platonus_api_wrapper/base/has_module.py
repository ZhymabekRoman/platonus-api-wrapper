from ..utils.base_cls_inject import inheritance_from_base_cls
from ..utils.loginizer import login_required
from ..utils.lru_cacher import timed_lru_cache


class HasModule:
    def __init__(self, base_cls):
        self.base_cls = base_cls

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def profile(self):
        response = self.session.get(self.api.has_module("student")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def journal(self):
        response = self.session.get(self.api.has_module("studentregister")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def current_journal(self):
        response = self.session.get(
            self.api.has_module("current_progress_gradebook_student")
        ).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def assignment(self):
        response = self.session.get(self.api.has_module("assignment")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def study_room(self):
        response = self.session.get(self.api.has_module("studyroom")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def messages(self):
        response = self.session.get(self.api.has_module("messages")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def user_auth(self):
        response = self.session.get(self.api.has_module("user_auth")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def release(self):
        response = self.session.get(self.api.has_module("release")).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def request_for_developers(self):
        response = self.session.get(
            self.api.has_module("request_for_developers")
        ).as_object()
        return response
