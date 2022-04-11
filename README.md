# OCaml Docset for Dash

This is an improved OCaml language / standard-library docset for [Dash](https://kapeli.com/dash).

Compared to Dash's official docset for OCaml, this one is [more up-to-date](https://github.com/frou/ocaml-docset/blob/master/Makefile#L1) and has better accuracy and usability too.

## Generating the Docset

You must have `python3` and `make` installed.

Clone this repository and then run `make` in its directory. The OCaml reference manual will automatically be downloaded, and then transformed into `./generated/ocaml-unofficial.docset`

## Installing the Docset

In the Dash application, choose `Preferences > Docsets > [+] > Add Local Docset` and select the generated docset mentioned above.
