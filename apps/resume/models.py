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

from apps.resume import storages
from utils.django.models import SafeDeleteModel, TimeStampedModel


class Resume(TimeStampedModel):
    # Info
    extra = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_('추가 정보'),
    )

    pdf_file = models.FileField(
        upload_to=storages.resume_pdf_upload,
        editable=True,
        null=True,
        verbose_name=_('프로필 이미지 파일'),
    )


    # Related
    user = models.OneToOneField(
        'member.User',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='resume',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('이력서')

        db_table = 'member_user_resume'

    def save(self, *args, **kwargs):
        if not self.id:
            rv = super(Resume, self).save(*args, **kwargs)
            MilitaryService.objects.create(resume_id=self.id)

            return rv

        old_instance = Resume.objects.filter(id=self.id).first()
        if not old_instance:
            return super(Resume, self).save(*args, **kwargs)

        # 업데이트
        rv = super(Resume, self).save(*args, **kwargs)

        return rv

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.user.name}>'


class Career(TimeStampedModel):
    class Position(DjangoChoices):
        staff = ChoiceItem('STAFF', _('스탭(인턴)'))
        manager = ChoiceItem('MANAGER', _('매니저'))
        designer = ChoiceItem('DESIGNER', _('디자이너'))
        director = ChoiceItem('DIRECTOR', _('원장'))

    # Info
    company = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('회사'),
    )

    position = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=Position.choices,
        verbose_name=_('직급'),
    )

    join_at = models.DateField(
        null=False,
        blank=False,
        verbose_name=_('입사일'),
    )

    quit_at = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('퇴사일'),
    )

    worked_on = models.CharField(
        max_length=500,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('업무 내용'),
    )

    # Related
    resume = models.ForeignKey(
        Resume,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='career_set',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('커리어')

        db_table = 'member_user_resume_career'

    @property
    def is_working(self):
        return not self.quit_at

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.resume.user.name}>'


class Certificate(TimeStampedModel):
    # Info
    name = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('이름'),
    )

    vendor = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('발급 기관'),
    )

    certificate_at = models.DateField(
        null=False,
        blank=False,
        verbose_name=_('취득일'),
    )

    # Related
    resume = models.ForeignKey(
        Resume,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='certificate_set',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('자격증')

        db_table = 'member_user_resume_certificate'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.resume.user.name}>'


class AcademicBackground(TimeStampedModel):
    # Info
    name = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('학교명'),
    )

    major = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('학과명'),
    )

    location = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('소재지'),
    )

    join_at = models.DateField(
        null=False,
        blank=True,
        verbose_name=_('입사일'),
    )

    quit_at = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('퇴사일'),
    )

    # Related
    resume = models.ForeignKey(
        Resume,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='academic_set',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('학력')

        db_table = 'member_user_resume_academic'

    @property
    def is_attending(self):
        return not self.quit_at

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.resume.user.name}>'


class MilitaryService(TimeStampedModel):
    class Status(DjangoChoices):
        not_applicable = ChoiceItem('NA', _('해당없음'))
        exemption = ChoiceItem('EXEMPTION', _('면제'))
        unfinished = ChoiceItem('UNFINISHED', _('미필'))
        finished = ChoiceItem('FINISHED', _('군필'))

    # Info
    service = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=Status.choices,
        verbose_name=_('병역'),
    )

    exemption_reason = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name=_('면제사유'),
    )

    join_at = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('입대일'),
    )

    quit_at = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('전역일'),
    )

    # Related
    resume = models.OneToOneField(
        Resume,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='military',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('병역')

        db_table = 'member_user_resume_military'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.resume.user.name}>'


class PictureCollection(TimeStampedModel):
    image_id = models.CharField(
        max_length=20,
        null=True,
    )

    url = models.URLField(
        max_length=200,
        null=False,
    )

    is_active = models.BooleanField(
        null=False,
        default=True,
    )

    # Related
    resume = models.ForeignKey(
        Resume,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='collection_set',
        verbose_name=_('이력서'),
    )

    class Meta:
        verbose_name = _('사진 모음')

        db_table = 'member_user_resume_picture_collection'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<{self._meta.verbose_name.title()}: {self.url}>'
