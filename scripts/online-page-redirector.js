// This is a "Serverless" / Cloud function that contains some supporting logic
// needed to make the "Open Online Page" and "Copy Online Page URL" Dash
// features work properly for this docset.
//
// The reason we need to do this is because the V3 redesign of the ocaml.org
// website changed things such that the URLs of pages in the online version of
// the manual no longer use the same directory structure as the .tar.gz version
// of the manual, which this docset is built from.

import { serve } from "https://deno.land/std@0.139.0/http/server.ts"

console.log("Listening on http://localhost:8000")
serve(_req => {
  return new Response("Hello Dash World!", {
    headers: { "content-type": "text/plain" },
  })
})
