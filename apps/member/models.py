from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
import uuid

# Create your models here.
class User(AbstractBaseUser, SafeDeleteModel, TimeStampedModel):
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
    nickname = models.CharField(
        max_length=20,
        null=True,
        blank=False,
        db_index=True,
        unique=True,
        verbose_name=_('닉네임')
    )
    picture = EFinderImageField(
        null=False,
        blank=False,
        attachment_type='ChatieUserPicture',
        verbose_name=_('사진')
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
    coin = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name=_('코인'),
        help_text=_('[주의] 코인은 정산과 관련있기 떄문에 변경에 주의하세요!')
    )

    # Paid Tap
    bronze_tap = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('브론즈 탭'),
        help_text=_('[주의] 정산과 관련있기 떄문에 변경에 주의하세요!')
    )
    silver_tap = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('실버 탭'),
        help_text=_('[주의] 정산과 관련있기 떄문에 변경에 주의하세요!')
    )
    gold_tap = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('골드 탭'),
        help_text=_('[주의] 정산과 관련있기 떄문에 변경에 주의하세요!')
    )
    donation_tap = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('후원 탭'),
        help_text=_('[주의] 정산과 관련있기 떄문에 변경에 주의하세요!')
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = _('회원')
        verbose_name_plural = _('회원 목록')

        indexes = [
            models.Index(fields=['deleted', 'is_active']),
        ]