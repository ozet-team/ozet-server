from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class EmployeeType(models.Model):
    name = models.CharField(max_length=32)


class Announcement(models.Model):
    class PayType(models.TextChoices):
        HOUR = "HO", "시급"
        DAY = "DA", "일급"
        WEEK = "WE", "주급"
        MONTH = "MO", "월급"
        YEAR = "YE", "연봉"
        IRRELEVANT = "IR", "무관"

    title = models.CharField("제목", max_length=128)
    shop_name = models.CharField("지점명", max_length=128)
    manager_name = models.CharField("담장자 이름", max_length=32)
    manager_phone_number = PhoneNumberField("담장자 전화번호", max_length=32)
    expired_datetime = models.DateField("마감일")
    working_hour_start = models.IntegerField("업무 시작시간")
    working_hour_end = models.IntegerField("업무 종료시간")
    pay_type = models.CharField("급여 종류", max_length=2, choices=PayType.choices)
    pay_amount = models.IntegerField("급여량")
    employee_types = models.ManyToManyField(
        EmployeeType,
        related_name="announcements",
    )
    description = models.TextField("상세내용", null=True, blank=True)