import logging

import requests
from allauth.account.decorators import login_required
from django.conf import settings
from django.contrib import auth
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)

SESSION_KEY_ACCESS_TOKEN = 'access_token'


@login_required
def index(request):
    return render(request, 'index.html')

def when_authorised_from_sso_provider(request):
    access_code = request.GET.get('code')
    logger.debug("We received an authorisation token from Staff SSO [" + access_code + "] ...")
    access_token = __get_access_token(request, access_code)
    __store_access_token_in_session(request, access_token)
    return redirect("/")


def logout(request):
    logger.debug("Logging out ...")
    __clear_session(request)
    sso_logout_uri = __get_sso_provider_url() + "/logout"
    logger.debug("Redirecting to [" + sso_logout_uri + "]")
    return redirect(sso_logout_uri)


def __clear_session(request):
    auth.logout(request)  # Clears the session cookie


# This is how we fetch the current profile.
def __store_access_token_in_session(request, access_token):
    request.session[SESSION_KEY_ACCESS_TOKEN] = access_token
    logger.debug("Added the access_token to the session.")


def __get_current_profile_as_json(request):
    if SESSION_KEY_ACCESS_TOKEN not in request.session:
        logger.debug("There is no access token stored in the session.")
        return None
    else:
        access_token = request.session[SESSION_KEY_ACCESS_TOKEN]
        logger.debug("There is an access token stored in the session.")
        logger.debug("We'll use it to get the current Profile ...")
        profile = __get_profile_as_json(access_token)
        if not profile:
            logger.debug("We failed to get the Profile, so we'll clear the session.")
            __clear_session(request)
            return None
        else:
            logger.debug("Yes, we are logged in, with Profile [" + str(profile) + "]")
            return profile


def __redirect_to_sso_provider(request):
    requested_scope = 'read write'
    state = 'kalle'
    response_type = 'code'
    provider_authorisation_url = __get_sso_provider_url() + '/o/authorize/'
    logging.debug("Attempting to get an authorisation code via [" + provider_authorisation_url + "] ...")

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


def __get_access_token(request, authorisation_code):
    token_request_url = __get_sso_provider_url() + '/o/token/'
    grant_type = 'authorization_code'
    logger.debug(
        "Attempting to get an access token from [" + token_request_url + "] for grant type [" + grant_type + "], using authorisation_code [" + authorisation_code + "] ...")
    response = requests.post(
        token_request_url,
        data={
            'grant_type': grant_type,
            'code': authorisation_code,
            'client_id': (__get_sso_client_id()),
            'client_secret': (__get_client_secret()),
            'redirect_uri': (__get_return_as_authorised_url(request)),
        }
    )

    if response.status_code == 200:
        access_token = response.json()['access_token']
        logger.debug("Successfully got an access token.")
        return access_token
    else:
        logger.error("Failed to get the access token. Status code was  [" + str(response.status_code) + "]")
        return None


def __get_profile_as_json(access_token):
    profile_url = __get_sso_provider_url() + '/api/v1/user/me/'
    authorisation_header_value = 'Bearer ' + access_token
    logger.debug("Attempting to get the current Profile via [" + profile_url + "] ....")
    response = requests.get(profile_url,
                            headers={
                                'Authorization': authorisation_header_value
                            })

    if response.status_code == 200:
        profile_as_json = response.json()
        logger.debug("Successfully got the Profile [" + str(profile_as_json) + "]")
        return profile_as_json
    else:
        logger.error("Unable to get the Profile. Status code was [" + str(response.status_code) + "]")
        return None
