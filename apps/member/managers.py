from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from safedelete.managers import SafeDeleteManager


class UserManager(BaseUserManager, SafeDeleteManager):
    def create_user(self, username, name=None, email=None, password=None):
        if not username:
            raise ValueError(_('아이디는 필수입니다.'))

        user = self.model(
            username=username,
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

    def create_superuser(self, username, name, password):
        u = self.create_user(username=username,
                             name=name,
                             password=password)
        u.is_admin = True
        u.is_registration = True

        u.save(using=self._db)

        return u
