import random
import string

CONFIRMATION_CODE_LEN = 10


def generate_confirmation_code():
    return ''.join(random.choices(
        string.digits + string.ascii_uppercase,
        k=CONFIRMATION_CODE_LEN))
