from ..utils.loginizer import login_required
from ..utils.lru_cacher import timed_lru_cache
from ..utils.dict2object import dict2object
from ..utils.base_cls_inject import inheritance_from_base_cls


class HasModule:
    def __init__(self, base_cls):
        self.base_cls = base_cls

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def profile(self):
        response = self.session.get(self.api.has_module("student")).json(object_hook=dict2object)
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def journal(self):
        response = self.session.get(self.api.has_module("studentregister")).json(object_hook=dict2object)
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def current_journal(self):
        response = self.session.get(self.api.has_module("current_progress_gradebook_student")).json(object_hook=dict2object)
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def assignment(self):
        response = self.session.get(self.api.has_module("assignment")).json(object_hook=dict2object)
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def study_room(self):
        response = self.session.get(self.api.has_module("studyroom")).json(object_hook=dict2object)
        return response
