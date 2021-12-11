from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumbers import PhoneNumber
from safedelete.managers import SafeDeleteManager


class UserManager(BaseUserManager, SafeDeleteManager):
    def create_user(
            self,
            username: str,
            phone_number: PhoneNumber,
            name: str = None,
            email: str = None,
            password: str = None
    ):
        if not username:
            raise ValueError(_('아이디는 필수입니다.'))

        if not phone_number:
            raise ValueError(_('전화번호는 필수입니다.'))

        user = self.model(
            username=username,
            phone_number=phone_number,
            name=None,
            email=None,
        )

        if name:
            user.name = name

        if email:
            user.email = email

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(self, username, phone_number, email, name, password):
        u = self.create_user(username=username,
                             phone_number=phone_number,
                             name=name,
                             email=email,
                             password=password)
        u.is_admin = True
        u.is_registration = True

        u.save(using=self._db)

        return u

    def get_by_natural_key(self, username):
        return self.get(username=username)
