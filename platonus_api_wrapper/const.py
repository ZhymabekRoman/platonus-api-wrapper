from dataclasses import dataclass
from enum import Enum
from typing import Dict, Literal, TypeAlias

LanguageCode: TypeAlias = Literal["ru", "en", "kz"]

LANGUAGE_MAPPING: Dict[LanguageCode, str] = {"ru": "1", "kz": "2", "en": "3"}

SUPPORTED_LANGUAGES: tuple[LanguageCode, ...] = tuple(LANGUAGE_MAPPING.keys())


class AuthType(str, Enum):
    LOGIN_PASSWORD = "1"
    LOGIN_PASSWORD_IIN = "2"
    PASSWORD_IIN = "3"
    NONE = "4"


@dataclass
class AuthRequirements:
    needs_login: bool
    needs_password: bool
    needs_iin: bool


AUTH_REQUIREMENTS: Dict[AuthType, AuthRequirements] = {
    AuthType.LOGIN_PASSWORD: AuthRequirements(True, True, False),
    AuthType.LOGIN_PASSWORD_IIN: AuthRequirements(True, True, True),
    AuthType.PASSWORD_IIN: AuthRequirements(False, True, True),
    AuthType.NONE: AuthRequirements(False, False, False),
}


MessageStatusItem: TypeAlias = dict[str, int | str]


class MessageStatus(str, Enum):
    ALL = "0"
        NEW = "1"
    VIEWED = "2"
    DELETED = "4"


MESSAGE_STATUS_MAPPING: Dict[MessageStatus, MessageStatusItem] = {
    MessageStatus.ALL: {"ID": 0, "name": "All"},
    MessageStatus.NEW: {"ID": 1, "name": "New"},
    MessageStatus.VIEWED: {"ID": 2, "name": "Viewed"},
    MessageStatus.DELETED: {"ID": 4, "name": "Deleted"},
}

SUPPORTED_MESSAGE_STATUSES: tuple[MessageStatus, ...] = tuple(
    MESSAGE_STATUS_MAPPING.keys()
)
