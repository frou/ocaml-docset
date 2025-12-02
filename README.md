# OCaml Docset for Dash

This is an alternative [Dash](https://kapeli.com/dash) docset for the [OCaml](https://ocaml.org) language and its standard-library.

<!-- @todo Use the stock docset again to remind myself of what it does and doesn't have -->
Compared to Dash's official docset for OCaml[^1], this one:

* [Is more up-to-date](https://github.com/frou/ocaml-docset/blob/master/Makefile#L1).
* Has better accuracy, in terms of which identifiers are successfully indexed and how they are categorized.
* Has better usability, e.g. the hierarchy of a page's sections is visualised in Dash's sidebar.

![Screenshot of Dash showing the Stdlib module in this docset](https://raw.githubusercontent.com/frou/ocaml-docset/master/screenshot.png)

<!-- @todo Check how the installation instructions in the README go when the stock OCaml docset is installed and enabled -->

## Generating the Docset

> [!IMPORTANT]
> The `python3`, `curl` and `make` commands must be available on your system.

Clone this repository and then run `make` in its directory. The OCaml reference manual will automatically be downloaded, and then transformed into `./generated/ocaml-unofficial.docset`

## Installing the Docset

In the Dash application, choose `Settings > Docsets > [+] > Add Local Docset` and select the generated docset mentioned above.

<!--
---

🎉 [See also the sibling docset for Standard ML (SML)](https://github.com/frou/sml-docset)
-->

[^1]: As far as I can tell, the code that generates Dash's official docset for OCaml is not open-source, so this one is not derived from it.
