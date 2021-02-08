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
