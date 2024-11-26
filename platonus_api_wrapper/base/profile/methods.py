from platonus_api_wrapper.base.profile.api import ProfileApiMethods
from platonus_api_wrapper.utils.base64 import Base64Converter
from platonus_api_wrapper.utils.base_cls_inject import inheritance_from_base_cls
from platonus_api_wrapper.utils.loginizer import login_required
from platonus_api_wrapper.utils.lru_cacher import timed_lru_cache


class Profile(object):
    def __init__(self, base_cls):
        self.base_cls = base_cls
        self.profile_api = ProfileApiMethods(
            base_cls.api.language_code, base_cls.api.rest_api_version
        )

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def person_fio(self):
        """Возвращает ФИО пользывателя"""
        response = self.session.get(self.api.person_fio)
        return response.text

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def person_id(self):
        """Возвращает ID пользывателя"""
        response = self.session.get(self.api.person_id).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def is_admin(self):
        response = self.session.get(self.api.is_admin).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    def profile_picture(self):
        """Возвращает аватарку пользывателя"""
        response = self.session.get(self.api.profile_picture).content
        return Base64Converter.decode(response)

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def person_type(self):
        """Возвращает тип пользывателя

        {"isPasswordExpired":false,"personType":1}
        """
        response = self.session.get(self.api.person_type).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(3600)
    def profile_info(self):
        """
        Возвращает информацию о текущем пользывателе
        Returns:
            lastName: Фамилия
            firstName: Имя
            patronymic: Отчество
            personType: Тип пользывателя - 1: Обучающиеся
                                           3: Преподаватель
                                           38: Родитель
            photoBase64: Фотография пользывателя в base64
            passwordExpired: Истек ли пароль пользывателя (bool значение)
            temporaryPassword: Стоит ли временный пароль (bool значение)
            studentID: ID обучающегося
            gpa: бог знает, скорее всего средняя оценка по всем урокам
            courseNumber: курс ученика
            groupName: название группы (потока)
            professionName: название специальности
            specializationName: название специализации
            studyTechnology: тип обучаемой технологии = 2 - по оценкам (5/4/3/2) (но это не точно)
        """
        response = self.session.get(self.api.profile_info).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(3600)
    def student_state_info(self):
        response = self.session.get(self.profile_api.student_state_info).as_object()
        return response

    @timed_lru_cache(86400)
    def person_type_list(self):
        """По идее должен возврящать список типов пользывателей Platonus, но почему-то ничего не возвращяет, нафиг его тогда  реализовали?!"""
        response = self.session.get(self.profile_api.person_type_list).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    async def upload_profile_picture(
        self,
        person_id: int,
        person_type: str,
        file_type: str,
        cropped_image: str,
        file=None,
        file_name: str = "cardPhoto.jpg",
        mime_type: str = "image/jpeg",
    ):
        """Upload a profile picture.

        Args:
            person_id: The ID of the person
            person_type: Type of the person (student, teacher, etc.)
            file_type: Type of the file being uploaded
            cropped_image: Base64 string of cropped image
            file: Optional file object for direct file uploads
            file_name: Name of the file (defaults to cardPhoto.jpg)
            mime_type: MIME type of the file (defaults to image/jpeg)

        Returns:
            Response from the upload endpoint
        """
        fields = {
            "personID": person_id,
            "personType": person_type,
            "fileType": file_type,
            "croppedImage": cropped_image,
            "fileName": file_name,
            "mime": mime_type,
        }

        if file:
            fields.update(
                {
                    "size": len(file.read()),
                    "fileName": file.name,
                    "mime": file.content_type,
                }
            )
            file.seek(0)

        return self.session.post(
            self.profile_api.upload_profile_picture,
            data=fields,
            files={"file": file} if file else None,
        ).as_object()
