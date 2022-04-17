from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# noinspection PyAbstractClass
class S3MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION


# noinspection PyAbstractClass
class S3StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


__all__ = (
    'S3StaticStorage',
    'S3MediaStorage',
)
