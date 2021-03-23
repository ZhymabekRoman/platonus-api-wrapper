import base64


def base64_encode(message: str) -> str:
    """Зашифровывает строку в base64"""
    return base64.b64encode(message)

    #message_bytes = message.encode('ascii')
    #base64_bytes = base64.b64encode(message_bytes)
    #base64_message = base64_bytes.decode('ascii')
    #return base64_message


def base64_decode(base64_message: str) -> str:
    """Расшифровывает base64 строку"""
    return  base64.b64decode(base64_message)

    #base64_bytes = base64_message.encode('ascii')
    #message_bytes = base64.b64decode(base64_bytes)
    #message = message_bytes.decode('ascii')
    #return message

