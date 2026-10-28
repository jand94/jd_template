import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

FAILURE = "Die Anfrage ist fehlgeschlagen."


def _detail(value):
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value)
    return str(value)


def _messages(value):
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return [_detail(item) for item in value.values()]
    return [str(value)]


def exception_handler(exc, context):
    """Formt API-Fehler so, wie der Frontend-Client sie liest.

    `detail` ist ein String. Jedes weitere Feld ist eine Liste von Strings.
    Unbehandelte Ausnahmen werden geloggt und ohne Interna beantwortet.
    """

    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception("Unbehandelte API-Ausnahme")
        return Response({"detail": FAILURE}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = response.data
    if isinstance(data, list):
        response.data = {"detail": _detail(data)}
        return response
    if not isinstance(data, dict):
        response.data = {"detail": _detail(data)}
        return response

    normalized = {}
    for key, value in data.items():
        if key == "detail":
            normalized["detail"] = _detail(value)
        else:
            normalized[key] = _messages(value)
    response.data = normalized
    return response
