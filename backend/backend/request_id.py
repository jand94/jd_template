import contextvars
import re
import uuid

_request_id = contextvars.ContextVar("request_id", default="-")
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def current_request_id():
    return _request_id.get()


class RequestIdMiddleware:
    """Setzt X-Request-ID und hält die Kennung für Logzeilen bereit."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get("X-Request-ID", "").strip()
        request_id = incoming if _SAFE_ID.fullmatch(incoming) else uuid.uuid4().hex
        request.request_id = request_id
        token = _request_id.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            _request_id.reset(token)
        response["X-Request-ID"] = request_id
        return response


class RequestIdFilter:
    def filter(self, record):
        request = getattr(record, "request", None)
        request_id = getattr(request, "request_id", None)
        # Django loggt 4xx/5xx erst nach der Middleware. Die Kennung steht
        # dann noch am Request, nicht mehr im Context.
        record.request_id = request_id or current_request_id()
        return True
