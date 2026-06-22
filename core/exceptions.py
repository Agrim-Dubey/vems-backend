import logging

from django.http import JsonResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        if isinstance(data, dict) and "detail" in data and len(data) == 1:
            response.data = {"message": str(data["detail"])}
        return response

    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {"message": "An unexpected error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def handler404(request, exception=None):
    return JsonResponse({"message": "Not found."}, status=404)


def handler500(request):
    return JsonResponse({"message": "An unexpected error occurred."}, status=500)
