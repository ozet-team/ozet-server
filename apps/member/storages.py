import os
from random import randint
from datetime import datetime


def profile_image_upload(instance: any, filename: str):
    filename_base, filename_ext = os.path.splitext(filename)

    root_dir = 'user/profile/'

    return f"{root_dir}/{instance.id}/{datetime.now().strftime('%Y%m%d')}_{str(randint(10000000, 99999999))}{filename_ext}"
