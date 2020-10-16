# OCaml 4.10.0 docset for Dash

This is an updated OCaml docset for [Dash](https://kapeli.com/dash).

Improvements over the original docset:

 * updated for OCaml version 4.10
 * constructors are indexed
 * functions are tagged as "function" instead of "value"
 * "core" library indexed
 * some fixes for operator indexing

## Building

    make

These commands will download the required reference manual file and create the
output docset and tarball in the `./target/` subfolder.
