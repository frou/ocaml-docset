# OCaml Docset for Dash

This is an alternative [Dash](https://kapeli.com/dash) docset for the [OCaml](https://ocaml.org) language and its standard-library.

<!-- @todo Use the stock docset again to remind myself of what it does and doesn't have -->
Compared to Dash's official docset for OCaml, this one:

* [Is more up-to-date](https://github.com/frou/ocaml-docset/blob/master/Makefile#L1).
* Has better accuracy, in terms of which identifiers are successfully indexed and how they are categorized.
* Has better usability, e.g. the hierarchy of the Sections within a page is preserved in the sidebar.


<!-- @todo Add screenshots to the README -->

<!-- @todo Check how the installation instructions in the README go when the stock OCaml docset is installed and enabled -->

## Generating the Docset

You must have `python3` and `make` installed.

Clone this repository and then run `make` in its directory. The OCaml reference manual will automatically be downloaded, and then transformed into `./generated/ocaml-unofficial.docset`

## Installing the Docset

In the Dash application, choose `Settings > Docsets > [+] > Add Local Docset` and select the generated docset mentioned above.

<!--
---

🎉 [See also the sibling docset for Standard ML (SML)](https://github.com/frou/sml-docset)
-->
