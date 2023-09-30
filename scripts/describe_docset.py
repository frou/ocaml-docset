import plistlib
import sys

(
    _,
    name,
    readable_name,
    search_keyword,
    main_page,
    online_page_base_url,
    output_path,
) = sys.argv

# REF: https://kapeli.com/docsets (search for "Info.plist")

info = {
    "CFBundleIdentifier": name,
    "CFBundleName": readable_name,
    # If the search keyword is already well-known to Dash, it will also be used to assign the docset's icon.
    "DocSetPlatformFamily": search_keyword,
    "isDashDocset": True,
    "dashIndexFilePath": main_page,
    "DashDocSetFamily": "dashtoc",
    "DashDocSetFallbackURL": online_page_base_url,
}

with open(output_path, "wb") as f:
    plistlib.dump(info, f)
