from platonus_api_wrapper.base.study_room.api import StudyRoomApi
from platonus_api_wrapper.utils.base_cls_inject import inheritance_from_base_cls
from platonus_api_wrapper.utils.loginizer import login_required
from platonus_api_wrapper.utils.memory_cacher import timed_lru_cache


class StudyRoom:
    def __init__(self, base_cls):
        self.base_cls = base_cls
        self.study_room_api = StudyRoomApi(
            base_cls.api,
        )

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(43200)
    def student_journal(self, year: int, term: int):
        """
        Возвращает журнал ученика
        Принимаемые аргументы: (см. также функцию study_years_list())
            year - год
            term - семестр
        """
        response = self.session.get(self.api.student_journal(year, term)).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(43200)
    def student_journal_records(self, year: int, term: int, subject_id: int):
        """
        Возвращает записи журнала ученика
        Принимаемые аргументы:
            year - год
            term - семестр
            subject_id - id предмета
        """
        response = self.session.get(
            self.api.student_journal_records(year, term, subject_id)
        ).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(43200)
    def report_without_appeal(self):
        response = self.session.get(self.api.report_without_appeal).as_object()
        return response
