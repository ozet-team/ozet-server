from django.contrib import admin
from apps.member.models import User, UserProfile, UserToken, UserPasscodeVerify

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserToken)
admin.site.register(UserPasscodeVerify)