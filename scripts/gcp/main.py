# This file defines a "Serverless Function" to run on https://cloud.google.com/functions/docs/
#
# It contains the supporting logic needed to make the "Open Online Page" and "Copy
# Online Page URL" features work properly in our Dash Docset.
#
# The reason we need to do any of this is that the 2022 redesign of the ocaml.org
# website changed things such that the URLs of pages in the online version of the manual
# no longer use the same directory structure as the .tar.gz version of the manual
# (which our Docset is generated from).
#
# For example:
#
# When the Docset is generated (using the Makefile), it is for a specific OCaml version,
# and the `DashDocSetFallbackURL` value in its Info.plist file is set to something like:
#
#     https://ocaml-docset-redirect.faas.frou.org/5.2/
#
# When a Dash user is viewing a page inside the Docset (such as the documentation for the
# Arg module in the standard library), and selects "Open Online Page" (by first clicking
# the Share icon at the top right), a URL like the following will be opened in their
# default web browser:
#
#     https://ocaml-docset-redirect.faas.frou.org/5.2/htmlman/libref/Arg.html
#
# The logic in this file will receive that HTTP request and will transform that URL into
# the following URL, and redirect to it:
#
#     https://ocaml.org/manual/5.2/api/Arg.html

import json
from enum import StrEnum, auto
from pathlib import Path
from urllib.parse import urlunsplit

import functions_framework
import werkzeug.routing as rt
from flask import Request, redirect
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException, MethodNotAllowed


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
        rt.Rule(
            "/<version>/htmlman/libref/<page>", methods=["GET"], endpoint=PageKind.API
        ),
        rt.Rule("/<version>/htmlman/<page>", methods=["GET"], endpoint=PageKind.PROSE),
    ]
)


@functions_framework.http
# REF(return type): https://flask.palletsprojects.com/en/3.0.x/quickstart/#about-responses
def transforming_redirect(request: Request) -> ResponseReturnValue:
    try:
        kind: PageKind
        kind, route_vars = ROUTES.bind_to_environ(request.environ).match()
    except MethodNotAllowed as e:
        # REF: https://werkzeug.palletsprojects.com/en/3.0.x/routing/#:~:text=All%20of%20the%20exceptions%20raised%20are%20subclasses%20of%20HTTPException%20so%20they%20can%20be%20used%20as%20WSGI%20responses
        return e
    except HTTPException:
        return (
            f'Unrecognised path. <a href="https://github.com/frou/ocaml-docset/blob/master/scripts/gcp/{Path(__file__).name}">See here</a> for an explanation of the purpose of this service, and open an issue if it is not working properly for you.',
            404,
        )

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
            log(LogSeverity.CRITICAL, slug=f"unhandled{PageKind.__name__}", kind=k)


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
