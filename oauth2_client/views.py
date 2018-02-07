import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView)

from .provider import StaffSSOProvider
from django.conf import settings

class StaffSSOAdapter(OAuth2Adapter):

    provider_id = StaffSSOProvider.id

    hostname = getattr(settings, 'DIT_SSO_HOSTNAME', 'sso.trade.uat.uktrade.io')
    access_token_url = 'https://{hostname}/o/token/'.format(hostname=hostname)
    authorize_url = 'https://{hostname}/o/authorize/'.format(hostname=hostname)
    supplier_url = 'https://{hostname}/api/v1/directory/supplier/'.format(hostname=hostname)
    profile_url = 'https://{hostname}/api/v1/user/me/'.format(hostname=hostname)

    def complete_login(self, request, app, token, **kwargs):
        print("login completed with token [" + token + "]")
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'alt': 'json'})
        resp.raise_for_status()
        extra_data = resp.json()

        headers = {'Authorization': 'Bearer {}'.format(token.token)}
        resp = requests.get(self.supplier_url,
                            headers=headers)
        try:
            extra_data.update(resp.json)
        except TypeError:
            pass
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login

    def get_callback_url(self, request,app):
        return "http://localhost:8000/authorised"

oauth2_login = OAuth2LoginView.adapter_view(StaffSSOAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StaffSSOAdapter)