from rest_framework.exceptions import ValidationError


def validate_pin(pin):
    if len(pin) < 4:
        raise ValidationError('Pin must be at least 4 digits')
