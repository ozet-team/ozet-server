from django.apps import AppConfig


class MemberConfig(AppConfig):
    name = 'apps.member'
    verbose_name = '회원'

    swagger_tag = dict(name='사용자 API 목록', description='')

    def ready(self):
        from . import signals
