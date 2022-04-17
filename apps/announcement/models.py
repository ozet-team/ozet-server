from enum import Enum

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class EmployeeType(models.Model):
    class Type(Enum):
        INTERN = "인턴(스텝)"
        MANAGER = "매니저"
        DESIGNER = "디자이너"
        CHIEF = "원장"

        @classmethod
        def get_type(cls, name: str):
            try:
                return cls(name)
            except ValueError as error:
                if name == "인턴":
                    return cls.INTERN
                raise error

    name = models.CharField(max_length=32)
    codename = models.CharField(max_length=16)


class Announcement(models.Model):
    class PayType(models.TextChoices):
        HOUR = "HO", "시급"
        DAY = "DA", "일급"
        WEEK = "WE", "주급"
        MONTH = "MO", "월급"
        YEAR = "YE", "연봉"
        IRRELEVANT = "IR", "무관"

    class ExpireType(models.TextChoices):
        ALWAYS = "AL", "상시모집"
        BASIC = "BA", "기본"
        FINISH = "FI", "충원시 마감"

    title = models.CharField("제목", max_length=128)
    shop_name = models.CharField("지점명", max_length=128)
    shop_location = models.CharField("지점 주소", max_length=256)
    city = models.ForeignKey("address.City", on_delete=models.PROTECT, related_name="+")
    country = models.ForeignKey(
        "address.Country", on_delete=models.PROTECT, related_name="+", null=True
    )
    manager_name = models.CharField("담장자 이름", max_length=32)
    manager_phone_number = PhoneNumberField("담장자 전화번호", max_length=32)
    expire_type = models.CharField("마감 타입", max_length=2, choices=ExpireType.choices)
    expired_datetime = models.DateTimeField("마감일", null=True, blank=True)
    working_hour = models.CharField("업무시간", max_length=128)
    pay_type = models.CharField("급여 종류", max_length=2, choices=PayType.choices)
    pay_amount = models.PositiveIntegerField("급여량")
    employee_types = models.ManyToManyField(
        EmployeeType,
        related_name="announcements",
    )
    description = models.TextField("상세내용", null=True, blank=True)
    external_id = models.IntegerField("외부 ID", null=True, db_index=True)
    image_url = models.URLField("이미지 URL", null=True)


class Bookmark(models.Model):
    user = models.ForeignKey(
        "member.User",
        on_delete=models.CASCADE,
        related_name="bookmark_set",
    )
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="bookmark_set",
    )
