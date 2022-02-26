import dataclasses
import datetime
import re
import time
from collections import defaultdict
from typing import Optional

from apps.address.models import City, Country
from apps.announcement.models import Announcement, EmployeeType
from django.core.management import BaseCommand
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

pay_info_pattern = re.compile(r"[(](.+)[)] (.+)")


class UnsupportedCountryException(BaseException):
    pass


@dataclasses.dataclass
class AnnouncementDTO:
    title: str
    shop_name: str
    manager_name: str
    manager_phone_number: str
    expire_type: Announcement.ExpireType
    expired_datetime: Optional[datetime.datetime]
    working_hour: str
    pay_type: Announcement.PayType
    pay_amount: int
    employee_types: list[EmployeeType.Type]
    description: str
    external_id: int
    shop_location: str
    city: City
    country: Optional[Country]
    image_url: Optional[str]


class Command(BaseCommand):
    login_info = {
        "id": "starismoon",
        "password": "ozet12345",
    }
    urls = {
        "login": "https://mimo.co.kr/mobile/login/login.php",
        "list": "https://mimo.co.kr/mobile/a5_job/sub-list-jung.php?cate=CATE150413170403&area=HR&table=guin",
        "detail": "https://mimo.co.kr/mobile/a5_job/guin-viewer.php?num=",
    }

    def handle(self, *args, **options):
        driver = Chrome(ChromeDriverManager().install())
        self.login(driver)

        self.cities_dict = self.get_cities_dict()
        self.countries_dict = self.get_countries_dict()

        dto_dict: dict[int, AnnouncementDTO] = {}
        for num in self.get_announcement_nums(driver, pages=5):
            try:
                dto_dict[num] = self.get_announcement(driver, num)
            except UnsupportedCountryException:
                continue

        announcement_dict = self.get_announcement_dict_by_nums(list(dto_dict.keys()))

        latest_announcement = Announcement.objects.order_by("id").last()
        latest_announcement_id = latest_announcement.id if latest_announcement else 0

        employee_type_dict = self.get_employee_type_dict()

        new_announcements = []
        new_announcement_employee_types_through_list = []

        for id, num in enumerate(
            set(dto_dict.keys()) - set(announcement_dict.keys()),
            start=latest_announcement_id + 1,
        ):
            dto = dto_dict[num]
            new_announcements.append(
                Announcement(
                    id=id,
                    title=dto.title,
                    shop_name=dto.shop_name,
                    shop_location=dto.shop_location,
                    manager_name=dto.manager_name,
                    manager_phone_number=dto.manager_phone_number,
                    expire_type=dto.expire_type,
                    expired_datetime=dto.expired_datetime,
                    working_hour=dto.working_hour,
                    pay_type=dto.pay_type,
                    pay_amount=dto.pay_amount,
                    description=dto.description,
                    external_id=dto.external_id,
                    city=dto.city,
                    country=dto.country,
                    image_url=dto.image_url,
                )
            )
            new_announcement_employee_types_through_list.extend(
                [
                    Announcement.employee_types.through(
                        announcement_id=id,
                        employeetype_id=employee_type_dict[employee_type].id,
                    )
                    for employee_type in dto.employee_types
                ]
            )

        Announcement.objects.bulk_create(new_announcements)
        Announcement.employee_types.through.objects.bulk_create(
            new_announcement_employee_types_through_list
        )

    def login(self, driver: Chrome):
        driver.get(self.urls["login"])
        driver.find_element(By.ID, "uId").send_keys(self.login_info["id"])
        driver.find_element(By.ID, "uPass").send_keys(self.login_info["password"])
        driver.find_element(By.ID, "loginBtn2").click()
        time.sleep(1)

    def get_announcement_nums(
        self, driver: Chrome, pages: int = 10, start_page: int = 0
    ) -> list[int]:
        nums = []

        for page in range(pages):
            page = page + start_page
            print("page:", page)
            driver.get(f"{self.urls['list']}#{page + 1}")
            time.sleep(1)
            for item in driver.find_element(By.ID, "boardList2").find_elements(
                By.TAG_NAME, "li"
            ):
                nums.append(int(item.get_attribute("data-num")))

        return nums

    def get_announcement(
        self,
        driver: Chrome,
        announcement_num: int,
    ) -> AnnouncementDTO:
        """
        `title: str
        `shop_name: str
        `manager_name: str
        `manager_phone_number: str
        `expired_datetime: datetime.datetime
        `working_hour_start: int
        `working_hour_end: int
        `pay_type: str
        `pay_amount: str
        `employee_types: list
        `description: str
        `external_id: int
        """
        print("announcement_num:", announcement_num)
        driver.get(f"{self.urls['detail']}{announcement_num}")
        time.sleep(0.2)

        # get title
        title_element = driver.find_element(By.CLASS_NAME, "jobTitle")
        title = title_element.text.replace(
            title_element.find_element(By.CLASS_NAME, "jobTitle-info").text, ""
        ).strip()

        # shop info
        shop_info_wrappers = driver.find_elements(By.CLASS_NAME, "shopInfo")

        classified_shop_info = self.get_classified_shop_info(shop_info_wrappers)

        shop_info_table = classified_shop_info["shop_info"].find_element(
            By.TAG_NAME, "table"
        )
        shop_info_rows = shop_info_table.find_elements(By.TAG_NAME, "tr")
        (
            shop_name_row,
            manager_name_row,
            manager_phone_row,
            shop_location_row,
        ) = shop_info_rows

        td = shop_name_row.find_element(By.TAG_NAME, "td")
        shop_name = td.find_element(By.TAG_NAME, "strong").text.strip()
        manager_name = manager_name_row.find_element(By.TAG_NAME, "td").text.strip()
        manager_phone = manager_phone_row.find_element(By.TAG_NAME, "td").text.strip()
        shop_location = shop_location_row.find_element(
            By.CLASS_NAME, "mapBtn"
        ).get_attribute("data-loc")

        city_name, left_address = shop_location.split(" ", 1)
        try:
            city = self.cities_dict[city_name]
        except KeyError:
            raise UnsupportedCountryException
        country = None
        for country_name in sorted(
            self.countries_dict[city].keys(), key=len, reverse=True
        ):
            if left_address.startswith(country_name):
                country = self.countries_dict[city][country_name]
                break

        if len(self.countries_dict[city].keys()) and country is None:
            raise ValueError(f"주소 정보를 찾을 수 없음: {shop_location}")

        # recruit info
        recruit_info_table = classified_shop_info["recruit_info"].find_element(
            By.TAG_NAME, "table"
        )
        recruit_info_rows = recruit_info_table.find_elements(By.TAG_NAME, "tr")
        (
            expired_datetime_row,
            employee_types_row,
            working_hour_row,
            pay_info_row,
        ) = recruit_info_rows
        expired_datetime = expired_datetime_row.find_element(
            By.TAG_NAME, "td"
        ).text.strip()
        expire_type = self.get_cleaned_expire_type(expired_datetime)

        if expire_type != Announcement.ExpireType.BASIC:
            expired_datetime = None

        working_hour = working_hour_row.find_element(By.TAG_NAME, "td").text.strip()
        # working_hour_start, working_hour_end = working_hour.split('~')
        # working_hour_start = int(working_hour_start.split(':')[0])
        # working_hour_end = int(working_hour_end.split(':')[0])

        employee_types = employee_types_row.find_element(By.TAG_NAME, "td").text.strip()
        employee_types = self.get_cleaned_employee_types(employee_types)

        pay_info = pay_info_row.find_element(By.TAG_NAME, "td").text.strip()
        pay_type, raw_pay_amount = pay_info_pattern.match(pay_info).groups()
        pay_type = self.get_claened_pay_type(pay_type)
        pay_amount = int(raw_pay_amount.split(" ")[0]) * 10_000

        # detail_info
        detail_info_table = classified_shop_info["detail_info"].find_element(
            By.TAG_NAME, "table"
        )
        description_article = detail_info_table.find_element(
            By.CLASS_NAME, "article"
        ).text.strip()

        # image
        try:
            attach_files = driver.find_element(By.CLASS_NAME, "attachFiles")
            first_image = attach_files.find_element(By.CLASS_NAME, "imgSize")
            image_url = f"https:{first_image.get_attribute('data-img')}"
        except NoSuchElementException:
            image_url = None

        return AnnouncementDTO(
            title=title,
            shop_name=shop_name,
            manager_name=manager_name,
            manager_phone_number=manager_phone,
            expire_type=expire_type,
            expired_datetime=expired_datetime,
            working_hour=working_hour,
            # working_hour_start=working_hour_start,
            # working_hour_end=working_hour_end,
            pay_type=pay_type,
            pay_amount=pay_amount,
            employee_types=employee_types,
            description=description_article,
            external_id=announcement_num,
            shop_location=shop_location,
            city=city,
            country=country,
            image_url=image_url,
        )

    def get_classified_shop_info(
        self, shop_info_elements: list
    ) -> dict[str, WebElement]:
        title_label_to_name = {
            "샵 정보": "shop_info",
            "채용정보": "recruit_info",
            "상세내용": "detail_info",
        }

        classified_shop_info = {}

        for shop_info_element in shop_info_elements:
            try:
                title_label = shop_info_element.find_element(
                    By.CLASS_NAME, "titleLabel"
                ).text.strip()
            except NoSuchElementException:
                continue

            if k := title_label_to_name.get(title_label):
                classified_shop_info[k] = shop_info_element

        return classified_shop_info

    def get_claened_pay_type(self, pay_type: str) -> Announcement.PayType:
        if pay_type == "시급":
            return Announcement.PayType.HOUR
        elif pay_type == "일급":
            return Announcement.PayType.DAY
        elif pay_type == "주급":
            return Announcement.PayType.WEEK
        elif pay_type == "월급":
            return Announcement.PayType.MONTH
        elif pay_type == "연봉":
            return Announcement.PayType.YEAR
        elif pay_type == "무관":
            return Announcement.PayType.IRRELEVANT

        raise ValueError(f"invalid pay type: {pay_type}")

    def get_cleaned_employee_types(
        self, employee_types: str
    ) -> list[EmployeeType.Type]:
        return [
            EmployeeType.Type.get_type(employee_type)
            for employee_type in employee_types.split("&")
            if employee_types
        ]

    def get_cleaned_expire_type(self, expire_time: str) -> Announcement.ExpireType:
        if expire_time == "충원시 마감":
            return Announcement.ExpireType.FINISH
        elif expire_time == "상시모집":
            return Announcement.ExpireType.ALWAYS

        return Announcement.ExpireType.BASIC

    def get_employee_type_dict(self) -> dict[EmployeeType.Type, EmployeeType]:
        return {
            getattr(EmployeeType.Type, employee_type.codename): employee_type
            for employee_type in EmployeeType.objects.all()
        }

    def get_announcement_dict_by_nums(self, nums: list[int]) -> dict[int, Announcement]:
        return {
            announcement.external_id: announcement
            for announcement in Announcement.objects.prefetch_related(
                "employee_types"
            ).filter(external_id__in=nums)
        }

    def get_cities_dict(self) -> dict[str, City]:
        return {city.name: city for city in City.objects.all()}

    def get_countries_dict(self) -> dict[City, dict[str, Country]]:
        countries_dict = defaultdict(dict)
        for country in Country.objects.select_related("city").all():
            countries_dict[country.city][country.name] = country

        return dict(countries_dict)
