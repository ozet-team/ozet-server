from django.conf import settings

from apps.member import views
from django.urls import path


urlpatterns = [
    path(
        "auth/passcode/request",
        views.UserPasscodeVerifyRequestView.as_view(),
        name=views.UserPasscodeVerifyRequestView.__name__,
    ),
    path(
        "auth/passcode/",
        views.UserPasscodeVerifyView.as_view(),
        name=views.UserPasscodeVerifyView.__name__,
    ),
    path(
        "user/me/",
        views.UserMeView.as_view(),
        name=views.UserMeView.__name__,
    ),
    path(
        "user/<int:user_id>/",
        views.UserDetailView.as_view(),
        name=views.UserDetailView.__name__,
    ),
    path(
        "user/<int:user_id>/instagram/",
        views.UserInstagramSocialListView.as_view(),
        name=views.UserInstagramSocialListView.__name__,
    ),
    path(
        "user/<int:user_id>/instagram/<int:social_id>/media/",
        views.UserInstagramMediaView.as_view(),
        name=views.UserInstagramMediaView.__name__,
    ),
    path(
        "user/<int:user_id>/instagram/<int:social_id>/media/collection",
        views.UserInstagramSocialImageCollectionView.as_view(),
        name=views.UserInstagramSocialImageCollectionView.__name__,
    ),
    path(
        "user/<int:user_id>/instagram/<int:social_id>/profile/",
        views.UserInstagramProfileView.as_view(),
        name=views.UserInstagramProfileView.__name__,
    ),
    path(
        "user/me/instagram/oauth/authorize/",
        views.UserInstagramOAuthView.as_view(),
        name=views.UserInstagramOAuthView.__name__,
    ),
    path(
        "user/me/instagram/oauth/cancel/",
        views.UserInstagramOAuthCancelView.as_view(),
        name=views.UserInstagramOAuthCancelView.__name__,
    ),
    path(
        "user/me/instagram/oauth/delete/",
        views.UserInstagramOAuthDeleteView.as_view(),
        name=views.UserInstagramOAuthDeleteView.__name__,
    ),
]

if settings.DEBUG:
    debug_urlpatterns = [
        path(
            "auth/passcode/pass/",
            views.UserPasscodeVerifyPassView.as_view(),
            name=views.UserPasscodeVerifyPassView.__name__,
        ),
        path(
            "auth/login/",
            views.UserTokenLoginView.as_view(),
            name=views.UserTokenLoginView.__name__,
        ),
        path(
            "auth/token/refresh/",
            views.UserTokenRefreshView.as_view(),
            name=views.UserTokenRefreshView.__name__,
        ),
        path(
            "user/",
            views.UserListView.as_view(),
            name=views.UserListView.__name__,
        ),
    ]

    urlpatterns += debug_urlpatterns
