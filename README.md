# OCaml docset for Dash

This is an improved OCaml docset for [Dash](https://kapeli.com/dash).

Compared to Dash's official docset for OCaml, this one is more up-to-date and has accuracy and usability improvements.

## Generating

You must have `python3` installed.

Run `make` and the official reference manual will automatically be downloaded, and then transformed into `./generated/ocaml-unofficial.docset`

## Installing

In the Dash application, choose `Preferences > Docsets > [+] > Add Local Docset` and select the generated docset mentioned above.
