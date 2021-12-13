from typing import Union
from datetime import datetime, timedelta
from random import randint

from djchoices import DjangoChoices, ChoiceItem
from model_utils.fields import AutoCreatedField
from phonenumber_field.modelfields import PhoneNumberField

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models, transaction
from rest_auth.utils import jwt_encode

from apps.member.models import User
from apps.resume import storages
from utils.django.models import SafeDeleteModel, TimeStampedModel


class Resume(TimeStampedModel):
    # info
    title = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('이력서 이름'),
    )

    pdf = models.FileField(
        upload_to=storages.resume_pdf_upload,
        editable=True,
        null=False,
        verbose_name=_('이력서 파일'),
    )

    extra = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_('추가 정보'),
    )

    # Fo
    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='resume_set',
        verbose_name=_('회원'),
    )

    class Meta:
        verbose_name = _('이력서')
        verbose_name_plural = _('이력서 목록')

        db_table = 'member_user_resume'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.title.name}>'