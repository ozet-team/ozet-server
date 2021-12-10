from typing import Union

from djchoices import DjangoChoices, ChoiceItem
from phonenumber_field.modelfields import PhoneNumberField

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models, transaction

from apps.member.managers import UserManager
from utils.django.models import SafeDeleteModel, TimeStampedModel


# Create your models here.
class User(AbstractBaseUser, SafeDeleteModel, TimeStampedModel):
    # info
    username = models.CharField(
        max_length=200,
        null=True,
        blank=False,
        db_index=True,
        unique=True,
        verbose_name=_('아이디')
    )
    email = models.EmailField(
        max_length=250,
        null=True,
        blank=False,
        db_index=True,
        verbose_name=_('이메일')
    )

    phone_number = PhoneNumberField(
        max_length=32,
        null=False,
        blank=False,
        verbose_name=_("전화번호"),
    )

    name = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        verbose_name=_('이름')
    )

    # config
    is_registration = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name=_('등록 완료 여부')
    )
    is_active = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name=_('활성화')
    )
    is_admin = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name=_('어드민')
    )

    # manager
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('회원')
        verbose_name_plural = _('회원 목록')

        indexes = [
            models.Index(fields=['deleted', 'is_active']),
        ]

        db_table = 'member_user'

    @property
    def get_latest_passcode_vertify(self):
        request_passcode_vertify = UserPasscodeVertify.objects \
            .filter(user=self) \
            .order_by('-created') \
            .first()

        return request_passcode_vertify

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.name}>'


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('회원'),
    )
    introduce = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('소개'),
    )

    extra = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_('추가 정보'),
    )

    class Meta:
        verbose_name = _('회원 프로필')
        verbose_name_plural = _('회원 프로필 목록')

        db_table = 'member_user_profile'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.user.name}>'


class UserPasscodeVertify(TimeStampedModel):
    """

    Notes:
        1. 클라이언트에서 서버에 패스코드 인증 요청 - GET
        2. 기존에 검증 대기중인 인증 요청이 있는지 확인 -> 없을 시 진행
            a. 만료되었을 경우 검증 대기중에서 -> 만료 됨 상태로 전환 -> 그대로 진행
            b. 검증 대기중이고 만료도 되지 않았을 경우 중복 검증 에러 반환
        3. 패스코드 인증 모델 생성
            a. 모델 생성시 전화번호가 일치하는 user 가 있을 경우 로그인 처리 -> 유저를 할당
            b. 없을 경우 회원가입 처리 -> 유저를 할당
        3. SMS 모듈을 통해서 사용자에게 패스코드가 포함된 메세지 전송
            a. 클라이언트에게 패스코드가 전송되었다는 응답을 보냄
        3.클라이언트가 전달받은 패스코드를 통해 인증 요청 - POST
        4.만료되지 않고 인증 대기중인 인증 요청의 패스코드와 API를 통해 전달되 패스코드가 동일할 경우 유저 토큰 반환
            a. 기존에 생성된 패스코드와 다를 경우 에러 응답
            b. 만료될 경우에는 그에 따른 에러 응답

    """
    class Status(DjangoChoices):
        vertified = ChoiceItem('used', label=_('완료된 검증'))
        pending = ChoiceItem('pending', label=_('검증 대기중'))
        expire = ChoiceItem('expire', label=_('만료 됨'))

    requester_phone_number = PhoneNumberField("요청자 전화번호", max_length=32)
    requsster_device_uuid = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('요청자 디바이스 UUID'),
    )

    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='auth_sms_set',
        verbose_name=_('인증되는 회원'),
    )

    passcode = models.CharField("패스코드", max_length=6)

    status = models.CharField(
        null=False,
        blank=False,
        max_length=20,
        default=Status.pending,
        choices=Status.choices,
        verbose_name=_('인증 상태'),
    )

    class Meta:
        verbose_name = _('회원 패스코드 인증 요청')
        verbose_name_plural = _('회원 패스코드 인증 요청')

        db_table = 'member_user_passcode_vertify'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.user.name}>'

    @classmethod
    def is_pending(cls, user: User) -> bool:
        latest_passcode_vertify = user.get_latest_passcode_vertify()

        return latest_passcode_vertify.status == cls.Status.pending

    @classmethod
    def vertify(
            cls,
            user: User,
            passcode: Union[int, str],
            is_transaction=True,
    ) -> bool:
        def __process():
            latest_passcode_vertify = user.get_latest_passcode_vertify()

            if latest_passcode_vertify and latest_passcode_vertify.passcode == passcode:
                latest_passcode_vertify.status = cls.Status.vertified
                latest_passcode_vertify.save()

                return True

            return False

        if is_transaction:
            with transaction.atomic():
                return __process()
        else:
            return __process()