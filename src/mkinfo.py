#!/usr/bin/env python3

import plistlib
import sys

_, name, readable_name, search_keyword, main_page = sys.argv

# REF: https://kapeli.com/docsets (search for "Info.plist")

d = {
    "CFBundleIdentifier": name,
    "CFBundleName": readable_name,
    # If the search keyword is already well-known to Dash, it will also be used to assign the docset's icon.
    "DocSetPlatformFamily": search_keyword,
    "isDashDocset": True,
    "dashIndexFilePath": main_page,
    "DashDocSetFamily": "dashtoc",
}

plistlib.dump(d, sys.stdout.buffer)

# @todo Get the "Open Online Page" functionality hooked up to use ocaml.org
# @body https://kapeli.com/docsets#onlineRedirection
# @body https://ocaml.org/releases/4.11/htmlman/index.html
# @body That functionality is actually already active, despite the key not being in the plist. But it goes through a Kapeli redirect and ends up at caml.inria.fr. I think this is because Dash natively has some knowledge of OCaml (due to the official outdated docset) that it's falling back on.
