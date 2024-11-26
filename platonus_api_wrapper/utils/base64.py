import base64


class Base64Converter:
    @staticmethod
    def encode(message: str) -> str:
        """Зашифровывает строку в base64"""
        return base64.b64encode(message.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode(base64_message: str) -> str:
        """Расшифровывает base64 строку"""
        return base64.b64decode(base64_message.encode("utf-8")).decode("utf-8")
