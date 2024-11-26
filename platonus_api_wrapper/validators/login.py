from typing import Any

from ..const import AUTH_REQUIREMENTS, AuthType
from ..utils import exceptions


def validate_login_credentials(auth_credentials: Any, auth_type: AuthType) -> bool:
    """Validates if the authorization credentials match the required authorization type.

    Platonus has 4 types of authorization:
    1) Login/Password
    2) Login/Password/IIN
    3) Password/IIN
    4) None

    Args:
        auth_credentials: Dictionary-like object containing authorization credentials
        auth_type: Platonus authorization type

    Raises:
        NotCorrectLoginCredentials: If credentials don't match the required format

    Returns:
        bool: True if credentials are valid
    """
    login = bool(getattr(auth_credentials, "login", None))
    password = bool(getattr(auth_credentials, "password", None))
    iin = bool(getattr(auth_credentials, "IIN", None))

    requirements = AUTH_REQUIREMENTS[auth_type]

    if (
        login != requirements.needs_login
        or password != requirements.needs_password
        or iin != requirements.needs_iin
    ):
        required_fields = []
        if requirements.needs_login:
            required_fields.append("login")
        if requirements.needs_password:
            required_fields.append("password")
        if requirements.needs_iin:
            required_fields.append("IIN")

        fields_msg = "/".join(required_fields) if required_fields else "no credentials"
        raise exceptions.NotCorrectLoginCredentials(
            f"Please provide exactly {fields_msg} for Platonus authorization"
        )

    return True
