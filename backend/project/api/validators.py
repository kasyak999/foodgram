import re
from rest_framework.serializers import ValidationError
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


# Пример регулярного выражения, которое вы можете использовать
PATTERN = r'^[\w.@+-]+$'


def validate_username(value):
    errors = []
    if value == 'me':
        errors.append(
            'Использовать имя "me" в качестве username запрещено')
    if not re.match(PATTERN, value):
        errors.append(
            'Может содержать только буквы, цифры и символы @/./+/-/_')
    if errors:
        raise ValidationError(errors)
    return value


def checking_avatar(value):
    """Декодирование base64 и создание файла изображения."""
    try:
        format, imgstr = value.split(';base64,')
        ext = format.split('/')[1]  # Получаем расширение файла
        imgdata = base64.b64decode(imgstr)  # Декодируем base64 в байты

        # Сохраняем изображение в виде файла
        Image.open(BytesIO(imgdata))
        file_name = f"avatar.{ext}"
        content_file = ContentFile(imgdata, name=file_name)
        return content_file
    except (ValueError, TypeError, ValidationError):
        raise ValidationError("Некорректный формат изображения.")
