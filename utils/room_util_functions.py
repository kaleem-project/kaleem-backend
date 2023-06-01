import random
from string import ascii_uppercase


def get_3chars():
    return ''.join(random.choice(ascii_uppercase) for i in range(3))


def generate_id():
    room_id = get_3chars() + "-" + get_3chars() + "-" + get_3chars()
    print(room_id)
