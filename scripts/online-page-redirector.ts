/*
This file defines a ""Serverless Function"" that comprises some supporting logic needed
to make the "Open Online Page" and "Copy Online Page URL" Dash features work properly
for the Docset.

The Deno Deploy platform notices when a new commit is made to the GitHub repo containing
this file and automatically redeploys it. REF: https://deno.com/deploy/docs/deployments

The reason we need to do any of this is that the 2022 redesign of the ocaml.org
website changed things such that the URLs of pages in the online version of the manual
no longer use the same directory structure as the .tar.gz version of the manual
(which our Docset is generated from).

For example:

When the Docset is generated (using the Makefile), it is for a specific OCaml version,
and the `DashDocSetFallbackURL` value in its Info.plist file is set to something like:

    https://ocaml-docset-redirector.deno.dev/5.2/

When a Dash user is viewing a page inside the Docset (such as the documentation for the
Arg module in the standard library), and selects "Open Online Page" (by first clicking
the Share icon at the top right), a URL like the following will be opened in their
default web browser:

    https://ocaml-docset-redirector.deno.dev/5.2/htmlman/libref/Arg.html

The logic in this file will receive that HTTP request and will transform that URL into
the following URL, and redirect to it:

    https://ocaml.org/manual/5.2/api/Arg.html
*/

import { Status } from "https://deno.land/std@0.178.0/http/http_status.ts"
import { ConnInfo, serve } from "https://deno.land/std@0.178.0/http/server.ts"
import * as path from "https://deno.land/std@0.178.0/path/mod.ts"

function makeDocUrl(ocamlVersion: string, ...docPathSegments: Array<string>): URL {
  // REF: https://github.com/ocaml/ocaml.org/issues/534#issuecomment-2112596837
  return new URL(
    ["manual", ocamlVersion, ...docPathSegments].join("/"),
    "https://ocaml.org"
  )
}

type Route = [URLPattern, (match: URLPatternResult) => Response]

const routes: Array<Route> = [
  [
    new URLPattern({ pathname: "/:version/htmlman/libref/:page" }),
    match =>
      Response.redirect(
        makeDocUrl(
          match.pathname.groups.version!,
          "api",
          match.pathname.groups.page!
        )
      ),
  ],
  [
    new URLPattern({ pathname: "/:version/htmlman/:page" }),
    match =>
      Response.redirect(
        makeDocUrl(
          match.pathname.groups.version!,
          "manual",
          match.pathname.groups.page!
        )
      ),
  ],
]

// NOTE: It seems to be an implementation detail of Deno Deploy that the contents of the
// GitHub repo linked to the Project appear to be placed under /src
const thisFileRepoRelPath = path.relative("/src", path.fromFileUrl(import.meta.url))

serve(function(req: Request, connInfo: ConnInfo) {
  for (const [pattern, respond] of routes) {
    const match = pattern.exec(req.url)
    if (match) {
      return respond(match)
    }
  }

  console.warn({
    unhandledUrlRequested: req.url,
    by: (connInfo.remoteAddr as Deno.NetAddr).hostname,
  })
  return new Response(
    `Unrecognised path. <a href="https://github.com/frou/ocaml-docset/blob/master/${thisFileRepoRelPath}">See here</a> for an explanation of the purpose of this service, and open an issue if it is not working properly for you.`,
    { status: Status.NotFound, headers: { "Content-Type": "text/html" } }
  )
})
