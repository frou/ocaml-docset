/*
This is a "Serverless"/Cloud function that contains some supporting logic needed to make
the "Open Online Page" and "Copy Online Page URL" Dash features work properly for this
Docset. The Deno Deploy platform notices when a new commit is made to the GitHub repo
and automatically redeploys this file. REF: https://deno.com/deploy/docs/deployments

The reason we need to do any of this is that the 2022 redesign ("V3") of the ocaml.org
website changed things such that the URLs of pages in the online version of the manual
no longer use the same directory structure as the .tar.gz version of the manual
(which our Docset is generated from).

For example:

When the Docset is generated (using the Makefie), it is for a specific OCaml version,
and the `DashDocSetFallbackURL` value in its Info.plist file is set to something like:

    https://ocaml-docset-redirector.deno.dev/4.14/

When a Dash user is viewing a page inside the Docset (such as the documentation for the
Arg module in the standard library), and selects "Open Online Page" (by first clicking
the Share icon at the top right), a URL like the folowing will be opened in their
default web browser:

    https://ocaml-docset-redirector.deno.dev/4.14/htmlman/libref/Arg.html

The logic in this file will receive that HTTP request and will transform that URL into
the following URL, and redirect to it:

    https://ocaml.org/releases/4.14/api/Arg.html
*/

import { serve } from "https://deno.land/std@0.139.0/http/server.ts"
import { Status } from "https://deno.land/std@0.139.0/http/http_status.ts"
// @todo Import the following from "npm:common-tags@^1.8.2" once Deno Deploy supports that feature.
import * as strTags from "https://esm.sh/common-tags@1.8.2"

const ocamlReleasesUrl = "https://ocaml.org/releases"
const selfExplainerUrl =
  "https://github.com/frou/ocaml-docset/blob/master/scripts/online-page-redirector.js"

const requestRoutes = [
  [
    new URLPattern({ pathname: "/:version/htmlman/libref/:page" }),
    match =>
      Response.redirect(
        `${ocamlReleasesUrl}/${match.pathname.groups.version}/api/${match.pathname.groups.page}`
      ),
  ],
  [
    new URLPattern({ pathname: "/:version/htmlman/:page" }),
    match =>
      Response.redirect(
        `${ocamlReleasesUrl}/${match.pathname.groups.version}/manual/${match.pathname.groups.page}`
      ),
  ],
]

serve(function (req, connInfo) {
  for (const [pattern, handler] of requestRoutes) {
    const match = pattern.exec(req.url)
    if (match) {
      return handler(match)
    }
  }

  console.warn({ unhandledUrlRequested: req.url, by: connInfo.remoteAddr.hostname })
  return new Response(
    strTags.oneLine`Unrecognised path. <a href="${selfExplainerUrl}">See here</a> for an
    explanation of the purpose of this service, and open an issue if it is not working
    properly for you.`,
    { status: Status.NotFound, headers: { "Content-Type": "text/html" } }
  )
})
