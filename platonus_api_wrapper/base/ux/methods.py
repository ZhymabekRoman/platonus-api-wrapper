import datetime
from typing import Literal

from platonus_api_wrapper.base.ux.api import UiApiMethods
from platonus_api_wrapper.const import MessageStatus
from platonus_api_wrapper.utils.base_cls_inject import inheritance_from_base_cls
from platonus_api_wrapper.utils.loginizer import login_required
from platonus_api_wrapper.utils.lru_cacher import timed_lru_cache


class UI(object):
    def __init__(self, base_cls):
        self.base_cls = base_cls
        self.ui_api = UiApiMethods(
            base_cls.api.language_code, base_cls.api.rest_api_version
        )

    @inheritance_from_base_cls
    @timed_lru_cache(86400)
    def has_for_visually_impaired_license(self):
        response = self.session.get(self.ui_api.has_for_visually_impaired_license)
        return response.as_object().hasLicense

    @inheritance_from_base_cls
    @timed_lru_cache(86400)
    def get_logo(self):
        response = self.session.get(self.ui_api.get_logo)
        return response.content

    @inheritance_from_base_cls
    @timed_lru_cache(3600)
    def has_unshown_release(self):
        response = self.session.get(self.ui_api.has_unshown_release).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(60)
    def survey_notifications(self):
        response = self.session.get(self.ui_api.survey_notifications).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(60)
    def notifications(self):
        response = self.session.get(self.ui_api.notifications).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(60)
    def system_messages_letters(self):
        response = self.session.get(self.ui_api.system_messages_letters).as_object()
        return response

    #
    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(60)
    def get_messages_by_params(
        self,
        status: MessageStatus = MessageStatus.NEW,
        period: datetime.date = datetime.date.today(),
        notification_category: Literal["all", ""] = "all",
        countInPart: int = 5,
        partNumber: int = 0,
    ):
        params = {
            "status": status,
            "period": period.strftime("%Y-%m-%d %Y-%m-%d"),
            "notification_category": notification_category,
            "countInPart": countInPart,
            "partNumber": partNumber,
        }
        response = self.session.get(
            self.ui_api.get_messages_by_params, params
        ).as_object()
        return response
