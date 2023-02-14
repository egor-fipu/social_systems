from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status


def custom_no_auth_handler(exc, context):
    if isinstance(exc, NotAuthenticated) or isinstance(exc, AuthenticationFailed):
        return Response(
            {'error': 'unauthorized'},
            status=status.HTTP_403_FORBIDDEN
        )

    return exception_handler(exc, context)
