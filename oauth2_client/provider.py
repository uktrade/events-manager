from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    PROFILE = 'profile'


class StaffSSOAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')


class StaffSSOProvider(OAuth2Provider):
    id = 'staff-sso'
    name = 'staff-sso'
    account_class = StaffSSOAccount

    def get_default_scope(self): return ['read write']

    def extract_uid(self, response):
        uid = response['id']
        return uid

    def extract_email_addresses(self, response):
        email = response.get('email', None)
        return [EmailAddress(email=email, verified=True)]

    def extract_common_fields(self, data):
        common_data = {}
        first_name = data.get('first_name')
        if first_name:
            common_data['first_name'] = first_name
        last_name = data.get('last_name')
        if last_name:
            common_data['last_name'] = last_name

        email = data.get('email')
        if email:
            common_data['email'] = email

        username = data.get('username', '_'.join([x for x in [first_name, last_name] if x]))
        if not username and email:
            username = email.split('@').pop(0)

        if username:
            common_data['username'] = username

        return common_data

    def get_auth_params(self, request, action):
        data = super(StaffSSOProvider, self).get_auth_params(request, action)
        data['state'] = 'kalle'
        return data


provider_classes = [StaffSSOProvider]
