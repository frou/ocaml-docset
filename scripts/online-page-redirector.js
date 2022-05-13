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
    return Response.error()
  }
})
