from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import StaffSSOProvider

urlpatterns = default_urlpatterns(StaffSSOProvider)


# /accounts/staff-sso/login/