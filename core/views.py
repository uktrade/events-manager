import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required()
def index(request):
    return render(request, 'index.html')


def login_via_sso_provider(request):
    if not request.user.is_authenticated:
        return __redirect_to_sso_provider(request)
    else:
        render(request, 'index.html')


def authorised(request):
    access_code = request.GET.get('code')
    access_token = __get_access_token(request, access_code)
    profile_as_json = __get_profile_as_json(access_token)
    email = profile_as_json['email']
    first_name = profile_as_json['first_name']
    last_name = profile_as_json['last_name']

    return render(request, 'index.html',
                  {
                      'first_name': first_name,
                      'last_name': last_name,
                      'email': email
                  })


def __redirect_to_sso_provider(request):
    requested_scope = 'read write'
    state = 'kalle'
    response_type = 'code'
    provider_authorisation_url = __get_sso_provider_url() + '/o/authorize/'
    url = '{url}?scope={scope}&state={state}&redirect_uri={redirect_uri}&response_type={response_type}&client_id={client_id}'.format(
        url=provider_authorisation_url,
        scope=requested_scope,
        state=state,
        redirect_uri=(__get_return_as_authorised_url(request)),
        response_type=response_type,
        client_id=(__get_sso_client_id())
    )
    return redirect(url)


def __get_sso_provider_url():
    return settings.SSO_PROVIDER


def __get_sso_client_id():
    return settings.SSO_CLIENT_ID


def __get_client_secret():
    return settings.SSO_CLIENT_SECRET


def __get_return_as_authorised_url(request):
    return settings.SSO_RETURNING_BASE_URI + '/authorised'


def __get_access_token(request, access_code):
    token_request_url = __get_sso_provider_url() + '/o/token/'
    grant_type = 'authorization_code'
    response = requests.post(
        token_request_url,
        data={
            'grant_type': grant_type,
            'code': access_code,
            'client_id': (__get_sso_client_id()),
            'client_secret': (__get_client_secret()),
            'redirect_uri': (__get_return_as_authorised_url(request)),
        }
    )

    assert response.status_code == 200
    access_token = response.json()['access_token']
    return access_token


def __get_profile_as_json(access_token):
    profile_url = __get_sso_provider_url() + '/api/v1/user/me/'
    authorisation_header_value = 'Bearer ' + access_token
    response = requests.get(profile_url,
                            headers={
                                'Authorization': authorisation_header_value
                            })

    assert response.status_code == 200
    profile_as_json = response.json()
    return profile_as_json
