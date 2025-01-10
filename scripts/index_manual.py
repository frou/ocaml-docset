import atexit
import logging
import re
import sqlite3
import sys
import urllib.parse
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Optional

# REF: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup, Tag

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)


# REF: https://kapeli.com/docsets#supportedentrytypes
class DashCategory(StrEnum):
    CONSTRUCTOR = auto()
    EXCEPTION = auto()
    FIELD = auto()
    FUNCTION = auto()
    INTERFACE = auto()
    LIBRARY = auto()
    MODULE = auto()
    SECTION = auto()
    TYPE = auto()
    VALUE = auto()
    # @todo Index the ~35 named Chapters as GUIDE


RE_LIBRARY_CHAPTER = re.compile(r".+The ([^ ]+) library(?:|: .+)")


def add_index(
    name: str,
    category: DashCategory,
    url_path: Path,
    url_fragment: Optional[str] = None,
) -> None:
    url = urllib.parse.urlunparse(("", "", str(url_path), "", "", url_fragment or ""))
    db.execute(
        """INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)""",
        (name, category.title(), url),
    )


STDLIB_MODULE_NAME = "Stdlib"
STDLIB_MODULE_PREFIX = STDLIB_MODULE_NAME + "."


def equivalent_unprefixed_stdlib_module_path(html_path: Path) -> Optional[Path]:
    if html_path.name.startswith(STDLIB_MODULE_PREFIX):
        unprefixed_html_path = html_path.parent / html_path.name.removeprefix(
            STDLIB_MODULE_PREFIX
        )
        if unprefixed_html_path.exists():
            return unprefixed_html_path
    return None


class Markup(BeautifulSoup):
    tweaked: bool  # Has the markup been modified such that it should be written back out to the file?

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.tweaked = False


def process_page(html_path: Path, html_internal_path: Path) -> Markup:
    with open(html_path) as f:
        soup = Markup(f, "html.parser")
    h1 = soup.find("h1")
    if not isinstance(h1, Tag):
        if not html_internal_path.name.startswith("type_"):
            logging.info("no h1 tag in %s", html_internal_path)
        return soup
    h1_content = list(h1.stripped_strings)
    libmatch = RE_LIBRARY_CHAPTER.fullmatch(" ".join(h1_content))

    if h1_content[0].startswith("Module") or h1_content[0] == "Functor":
        if h1_content[0] == "Module type":
            category = DashCategory.INTERFACE
        else:
            category = DashCategory.MODULE
        module_name = h1_content[1]

        # Add a page ToC entry for the module's own name, because otherwise when the page is
        # scrolled down some, it can be unclear precisely which module is being viewed.
        h1.insert_before(anchor_element(soup, category, module_name))

        if (
            # Skip processing the documentation for some modules, because inserting
            # their information into the Index would cause effective duplicates.
            #
            # The module "Pervasives" was superseded by "Stdlib" in OCaml 4.07,
            # deprecated in 4.08, and removed in 5.0.
            # By skipping it, we avoid for example having both `Stdlib.at_exit` and
            # `Pervasives.at_exit` in the Index for the same function.
            module_name in ["Pervasives", STDLIB_MODULE_PREFIX + "Pervasives"]
            # For most modules named `Stdlib.Foo`, the manual also contains
            # documentation for it as module `Foo`. Skip the former because it's noisier.
            or (
                module_name.startswith(STDLIB_MODULE_PREFIX)
                # It's not always that an equivalent `Foo` module exists, so check the
                # filesystem.
                and equivalent_unprefixed_stdlib_module_path(html_path)
            )
            # A module named named `StdLabels.Foo` is just a re-export of a `FooLabels`
            # module which will already be processed.
            or module_name.startswith("StdLabels.")
            # Skip modules with names starting with this prefix because they are billed
            # as "for system use only".
            or module_name.startswith("Camlinternal")
        ):
            return soup

        add_index(module_name, category, html_internal_path)
        handle_module(html_internal_path, module_name, soup)
        return soup
    elif libmatch is not None:
        libname = libmatch.group(1)
        # REF: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#multi-valued-attributes
        (id_val,) = h1.get_attribute_list("id")
        add_index(libname, DashCategory.LIBRARY, html_internal_path, id_val)
        handle_library(html_internal_path, libname, soup)
        return soup
    else:
        if not html_internal_path.name.startswith("index_"):
            logging.info("no recognisable library or module in %s", html_internal_path)
        return soup


# @todo Every time this function is used, its result is passed to soup's insert_before(...), so just integrate that into this function, and rename this function to mention ToC.
def anchor_element(soup: Markup, category: DashCategory, id_: str) -> Tag:
    id_quoted = urllib.parse.quote(id_, safe="")
    a = soup.new_tag("a")
    a.attrs["name"] = f"//apple_ref/cpp/{category.title()}/{id_quoted}"
    a.attrs["class"] = "dashAnchor"
    soup.tweaked = True
    return a


# REF: https://ocaml.org/releases/4.10/htmlman/lex.html#sss:lex:identifiers
RE_IDENTIFIER_COMMON_TAIL = r"[A-Za-z0-9_']*"
RE_IDENTIFIER = rf"[A-Za-z_]{RE_IDENTIFIER_COMMON_TAIL}"
RE_IDENTIFIER_CAPITALIZED = rf"[A-Z]{RE_IDENTIFIER_COMMON_TAIL}"
RE_IDENTIFIER_LOWERCASE = rf"[a-z_]{RE_IDENTIFIER_COMMON_TAIL}"
# REF: https://ocaml.org/releases/4.10/htmlman/types.html#sss:typexpr-variables
RE_TYPE_VARIABLE = rf"'{RE_IDENTIFIER}"
# REF: https://ocaml.org/releases/4.10/htmlman/names.html#sss:refer-named
RE_TYPE_NAME = RE_IDENTIFIER_LOWERCASE
RE_EXCEPTION_NAME = RE_IDENTIFIER_CAPITALIZED

RE_LIB_DOCUMENTATION_OF_TYPE = re.compile(
    rf"type (?:(?:{RE_TYPE_VARIABLE}|\({RE_TYPE_VARIABLE}(?:, {RE_TYPE_VARIABLE})*\)) )?({RE_TYPE_NAME})(?: = (\S+(?: \| .+)?))?"
)
RE_LIB_DOCUMENTATION_OF_EXCEPTION = re.compile(
    rf"exception ({RE_EXCEPTION_NAME})(?: of .+)?"
)


def handle_library(html_internal_path: Path, _library_name: str, soup: Markup) -> None:
    next_id = {"id": 0}

    def autoid() -> str:
        id_, next_id["id"] = next_id["id"], next_id["id"] + 1
        return f"autoid_{id_:04x}"

    def getid(element: Tag) -> str:
        # NOTE: Can't just use `element["id"]` because types say that attributes can have multiple
        #       values: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#multi-valued-attributes
        (id_val,) = element.get_attribute_list("id")
        if id_val is None:
            element["id"] = (id_val := autoid())
            soup.tweaked = True
        return id_val

    for pre in soup.find_all("pre"):
        pretext = " ".join(pre.stripped_strings)
        m_type = RE_LIB_DOCUMENTATION_OF_TYPE.fullmatch(pretext)
        if m_type is not None:
            typname = m_type.group(1)
            add_index(typname, DashCategory.TYPE, html_internal_path, getid(pre))
            pre.insert_before(anchor_element(soup, DashCategory.TYPE, typname))

            all_ctors = m_type.group(2)
            if all_ctors:
                for ctor in all_ctors.split("|"):
                    ctor_name = ctor.split()[0]
                    add_index(
                        ctor_name,
                        DashCategory.CONSTRUCTOR,
                        html_internal_path,
                        getid(pre),
                    )
                    pre.insert_before(
                        anchor_element(soup, DashCategory.CONSTRUCTOR, ctor_name)
                    )
            continue

        m_exn = RE_LIB_DOCUMENTATION_OF_EXCEPTION.fullmatch(pretext)
        if m_exn is not None:
            exnname = m_exn.group(1)
            add_index(exnname, DashCategory.EXCEPTION, html_internal_path, getid(pre))
            pre.insert_before(anchor_element(soup, DashCategory.EXCEPTION, exnname))
            continue


TEE_PREFIX = "t."


def handle_module(html_internal_path: Path, module_name: str, soup: Markup) -> None:  # noqa: C901
    major_section = None
    for section_header in soup.find_all(["h2", "h3"]):
        if section_header.name == "h2":
            major_section = section_header.string
            add_index(
                f"{module_name} — {major_section}",
                DashCategory.SECTION,
                html_internal_path,
                section_header["id"],
            )
            section_header.insert_before(
                anchor_element(soup, DashCategory.SECTION, major_section)
            )
        elif section_header.name == "h3":
            minor_section = section_header.string

            index_parent_section_prefix, toc_indent = "", ""
            if major_section is None:
                logging.warning(
                    "minor section (%s) not preceded by major in %s",
                    minor_section,
                    html_internal_path,
                )
            else:
                index_parent_section_prefix = f" — {major_section}"
                toc_indent = "\t"

            add_index(
                f"{module_name}{index_parent_section_prefix} — {minor_section}",
                DashCategory.SECTION,
                html_internal_path,
                section_header["id"],
            )
            section_header.insert_before(
                anchor_element(
                    soup, DashCategory.SECTION, f"{toc_indent}{minor_section}"
                )
            )

    for span in soup.find_all("span", id=True):
        spanid = span["id"]
        if spanid.startswith("TYPEELT"):
            name = spanid[7:]
            # this can either be a constructor or a record field
            # full_code = ' '.join(span.parent.stripped_strings)
            if module_name == "Bool" and name in [
                TEE_PREFIX + "false",
                TEE_PREFIX + "true",
            ]:
                # The bool variant type has unusual constructors (they start with a lowercase letter).
                category = DashCategory.CONSTRUCTOR
            elif name.split(".")[-1][0].islower():
                category = DashCategory.FIELD
            else:
                category = DashCategory.CONSTRUCTOR
            if module_name == "Unit" and name == "t.()":
                # `Unit.t.()` shows as `Unit.t.` in the Dash search bar (index). Is Dash
                # trying to be smart and trimming off the trailing `()` because it looks
                # like a function call? Work around that by adding a unicode Zero Width
                # Space between the parentheses.
                add_index(
                    f"{module_name}.{name[:3]}\u200b{name[3]}",
                    category,
                    html_internal_path,
                    spanid,
                )
            else:
                add_index(f"{module_name}.{name}", category, html_internal_path, spanid)
            span.parent.insert_before(
                anchor_element(
                    soup,
                    category,
                    # In the sidebar (ToC), display constructor names from a module's
                    # primary type (`type t` by convention) in a cleaner way.
                    name[len(TEE_PREFIX) :] if name.startswith(TEE_PREFIX) else name,
                )
            )

        elif spanid.startswith("TYPE"):
            name = spanid[4:]
            span.parent.insert_before(anchor_element(soup, DashCategory.TYPE, name))
            add_index(
                f"{module_name}.{name}", DashCategory.TYPE, html_internal_path, spanid
            )
        elif spanid.startswith("EXCEPTION"):
            name = spanid[9:]
            add_index(
                f"{module_name}.{name}",
                DashCategory.EXCEPTION,
                html_internal_path,
                spanid,
            )
            span.parent.insert_before(
                anchor_element(soup, DashCategory.EXCEPTION, name)
            )
        elif spanid.startswith("VAL"):
            name = spanid[3:]
            if any("->" in s for s in span.parent.strings):
                category = DashCategory.FUNCTION
            else:
                category = DashCategory.VALUE
            add_index(f"{module_name}.{name}", category, html_internal_path, spanid)
            span.parent.insert_before(anchor_element(soup, category, name))
        # On the Stdlib module's page, nullify the links to its submodules at the
        # bottom, which point to e.g. "Stdlib.Foo.html". Right next to them remain
        # clickable links to distinct pages that document those modules in unprefixed
        # form, e.g. "Foo.html". We do this because we do not index or create sidebars
        # (ToCs) for the "Stdlib.Foo.html" pages because they are effectively duplicate
        # content.
        #
        # @todo Instead of nullifying the first link, instead modify it and remove what comes after
        # @body i.e. `module Bool: Bool` becomes just `module Bool`
        # @body Also, rename the section from "Standard library modules" to "Submodules of Stdlib", since the list doesn't include the Stdlib module itself?
        # @body The section is also mentioned in the blurb at the very top of the page.
        elif module_name == STDLIB_MODULE_NAME and spanid.startswith("MODULE"):
            if a := span.find("a"):
                try:
                    del a["href"]
                except KeyError:
                    pass


# ------------------------------------------------------------

docset_documents_path, docset_indexdb_path = (Path(arg) for arg in sys.argv[1:])

docset_indexdb_path.unlink(missing_ok=True)
db = sqlite3.connect(docset_indexdb_path)
atexit.register(db.close)
atexit.register(db.commit)
db.execute(
    "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)"
)
db.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)")

for page_path in [
    path
    for path in Path(docset_documents_path).rglob("*.html")
    # "This library is part of the internal OCaml compiler API, and is not the language standard library."
    if not path.match("**/compilerlibref/*")
]:
    page_markup = process_page(page_path, page_path.relative_to(docset_documents_path))
    if page_markup.tweaked:
        with open(page_path, "w") as f:
            f.write(str(page_markup))

# @todo Log something like "<n> OCaml entities were indexed for the Docset"
# @→    Based on the row count of the table.
