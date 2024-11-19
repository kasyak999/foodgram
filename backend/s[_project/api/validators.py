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
