from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.member.managers import UserManager
from utils.django.models import SafeDeleteModel, TimeStampedModel


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

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = _('회원')
        verbose_name_plural = _('회원 목록')

        indexes = [
            models.Index(fields=['deleted', 'is_active']),
        ]

        db_table = 'member_user'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.nickname}>'


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
