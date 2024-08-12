import re
from django.core.exceptions import ValidationError

def validate_username(value):
    if re.fullmatch(r'\d+', value):
        raise ValidationError('Username cannot consist of only numbers.')
