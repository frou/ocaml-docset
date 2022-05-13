// This is a "Serverless" / Cloud function that contains some supporting logic
// needed to make the "Open Online Page" and "Copy Online Page URL" Dash
// features work properly for this docset.
//
// REF: https://deno.com/deploy/docs

// The reason we need to do this is because the 2022 redesign ("V3") of the
// ocaml.org website changed things such that the URLs of pages in the online
// version of the manual no longer use the same directory structure as
// the .tar.gz version of the manual, which this docset is built from.

import { serve } from "https://deno.land/std@0.139.0/http/server.ts"
import {
  Status,
  STATUS_TEXT,
} from "https://deno.land/std@0.139.0/http/http_status.ts"
import * as strTags from "https://cdn.skypack.dev/common-tags@1.8.2?dts"

const reqPathLibraryPagePattern = new URLPattern({
  pathname: "/:version/htmlman/libref/:page",
})
const reqPathOtherPagePattern = new URLPattern({
  pathname: "/:version/htmlman/:page",
})

const respUrlPrefix = "https://ocaml.org/releases"

serve(req => {
  let match = reqPathLibraryPagePattern.exec(req.url)
  if (match) {
    return Response.redirect(
      `${respUrlPrefix}/${match.pathname.groups.version}/api/${match.pathname.groups.page}`
    )
  } else if ((match = reqPathOtherPagePattern.exec(req.url))) {
    return Response.redirect(
      `${respUrlPrefix}/${match.pathname.groups.version}/manual/${match.pathname.groups.page}`
    )
  } else {
    const statusCode = Status.NotFound
    return new Response(
      strTags.oneLine`If you arrived here via the 'Open Online Page' or
'Copy Online Page URL' feature in Dash, then this should have worked.
Please open a new issue at https://github.com/frou/ocaml-docset/issues
saying which page of the docset you were trying to view.`,
      {
        headers: { "content-type": "text/plain" },
        status: statusCode,
        statusText: STATUS_TEXT.get(statusCode),
      }
    )
  }
})
