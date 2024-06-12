import json
from enum import StrEnum, auto
from urllib.parse import urlunsplit

import functions_framework
import werkzeug.routing as rt
from flask import Request, redirect
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException


class PageKind(StrEnum):
    API = auto()
    PROSE = auto()


# Cloud Functions (for the Python runtime) use Flask but are not written as full-blown
# Flask "app"s. Because of that, we can't define routing in the normal Flask way and so
# need to drop down to this level.
#
# REF: https://werkzeug.palletsprojects.com/en/3.0.x/routing/
ROUTES = rt.Map(
    [
        rt.Rule("/<version>/htmlman/libref/<page>", endpoint=PageKind.API),
        rt.Rule("/<version>/htmlman/<page>", endpoint=PageKind.PROSE),
    ]
)


@functions_framework.http
# REF(return type): https://flask.palletsprojects.com/en/3.0.x/quickstart/#about-responses
def transforming_redirect(request: Request) -> ResponseReturnValue:
    try:
        kind: PageKind
        kind, route_vars = ROUTES.bind_to_environ(request.environ).match()
    except HTTPException as e:
        # REF: https://werkzeug.palletsprojects.com/en/3.0.x/routing/#:~:text=A%20NotFound%20exception%20is%20also%20a%20WSGI%20application
        return e

    match kind:
        case PageKind.API:
            return redirect(
                manual_url(request, route_vars["version"], "api", route_vars["page"])
            )
        case PageKind.PROSE:
            return redirect(
                manual_url(request, route_vars["version"], route_vars["page"])
            )
        case k:
            log(LogSeverity.CRITICAL, slug=f"unrecognised{PageKind.__name__}", kind=k)

    # @todo Show a message to the browser user encouraging them to report a bug.


# Build a manual URL using the modern ocaml.org URL structure.
# REF: https://github.com/ocaml/ocaml.org/issues/534#issuecomment-2112596837
def manual_url(req: Request, ocaml_version: str, *path_segments: str) -> str:
    return urlunsplit(
        (
            "https",
            "ocaml.org",
            "/".join(["manual", ocaml_version, *path_segments]),
            req.query_string.decode(),
            # NOTE: Browsers do not send a #fragment part of a URL to the webserver when
            # making a request. However, browsers are smart about restoring a fragment
            # clientside after a redirect. REF: https://stackoverflow.com/a/2305927/82
            None,
        )
    )


# ------------------------------------------------------------


# REF: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity
class LogSeverity(StrEnum):
    # DEFAULT = auto()
    DEBUG = auto()
    INFO = auto()
    NOTICE = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    ALERT = auto()
    EMERGENCY = auto()


# REF: https://cloud.google.com/functions/docs/monitoring/logging#writing_structured_logs
# REF: https://cloud.google.com/logging/docs/agent/logging/configuration#special-fields
def log(severity: LogSeverity, *, slug: str, **kwargs: object) -> None:
    print(json.dumps(dict(severity=severity, message=slug, **kwargs)))  # noqa: T201
