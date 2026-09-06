import re
import unicodedata

from bs4 import BeautifulSoup, Tag

with open(
    "generated/ocaml-unofficial.docset/Contents/Resources/Documents/htmlman/index.html"
) as f:
    soup = BeautifulSoup(f, "html.parser")


def cleaned_text(tag: Tag) -> str:
    "Replace e.g. U+00A0 (No-Break Space) and U+2003 (Em Space) with normal spaces"
    return unicodedata.normalize("NFKD", tag.get_text())


for table in soup.find_all("table"):
    part_title = cleaned_text(table).splitlines()[1]
    if part_title not in {
        "An introduction to OCaml",
        "The OCaml language",
        "The OCaml tools",
    }:
        continue

    print(part_title)
    part_chapters = table.find_next_sibling("ul")
    for chapter_link in part_chapters.find_all("a"):
        href = chapter_link.attrs["href"]
        text = re.sub(r"^Chapter \d+ ", "", cleaned_text(chapter_link))
        print(href, "\t", text)
    print()
