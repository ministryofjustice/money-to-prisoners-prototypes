import base64
from urllib.parse import unquote_plus

from django.conf import settings
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare


class BasicAuthorisationMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if not self.is_authorised(request):
            response = HttpResponse('Authorisation required', content_type='text/plain', status=401)
            response['WWW-Authenticate'] = 'Basic realm="mtp"'
            return response
        return self.get_response(request)

    def is_authorised(self, request):
        if not settings.BASIC_AUTH_USERNAME or not settings.BASIC_AUTH_PASSWORD:
            return True
        authorisation = request.META.get('HTTP_AUTHORIZATION', '')
        authorisation = authorisation.split(' ')
        if not len(authorisation) == 2:
            return False
        authorisation_type, authorisation_hash = authorisation
        if authorisation_type.lower() != 'basic':
            return False
        try:
            authorisation = base64.b64decode(authorisation_hash).decode()
        except UnicodeDecodeError:
            return False
        authorisation = authorisation.split(':')
        if not len(authorisation) == 2:
            return False
        username, password = map(unquote_plus, authorisation)
        return constant_time_compare(username, settings.BASIC_AUTH_USERNAME) and \
            constant_time_compare(password, settings.BASIC_AUTH_PASSWORD)
