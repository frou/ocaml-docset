#!/usr/bin/env python3

import os
import re
import sqlite3
import urllib.parse
from fnmatch import fnmatch

from bs4 import BeautifulSoup

TYPE_CONSTRUCTOR = 'Constructor'
TYPE_EXCEPTION   = 'Exception'
TYPE_FIELD       = 'Field'
TYPE_FUNCTION    = 'Function'
TYPE_LIBRARY     = 'Library'
TYPE_MODULE      = 'Module'
TYPE_TYPE        = 'Type'
TYPE_VALUE       = 'Value'

RE_LIBRARY_CHAPTER = re.compile(r'.+The ([^ ]+) library(?:|: .+)')

def add_index(name, typ, path):
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)''',
              (name, typ, path))
    conn.commit()
    # print(f'{name:32s}  {typ:12s}  {path}')

def contains(node, string):
    for s in node.strings:
        if string in s:
            return True
    return False

def run(filename, file_path):
    with open(file_path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    soup.made_changes = False
    h1 = soup.find('h1')
    if h1 is None:
        if not os.path.basename(filename).startswith('type_'):
            print('WARN: no h1: ' + filename)
        return soup, []
    h1_content = list(h1.stripped_strings)
    libmatch = RE_LIBRARY_CHAPTER.fullmatch(' '.join(h1_content))
    def anchor(id):
        return filename + '#' + id

    if h1_content[0].startswith('Module') or h1_content[0].startswith('Functor'):
        module_name = h1_content[1]
        if module_name == "Pervasives" or module_name.startswith("Stdlib."):
            return soup, []
        add_index(module_name, TYPE_MODULE, filename)
        handle_module(filename, module_name, soup)
        return soup, []
    elif libmatch is not None:
        libname = libmatch.group(1)
        add_index(libname, TYPE_LIBRARY, anchor(h1['id']))
        handle_library(filename, libname, soup)
        return soup, []
    else:
        if not os.path.basename(filename).startswith('index_'):
            print('WARN: no module: ' + filename)
        return soup, []

def anchor_element(soup, typ, id):
    id_quoted = urllib.parse.quote(id, safe='')
    a = soup.new_tag('a')
    a.attrs['name'] = f'//apple_ref/cpp/{typ}/{id_quoted}'
    a.attrs['class'] = 'dashAnchor'
    soup.made_changes = True
    return a

RE_LIB_TYPE = re.compile(r'type (?:.+ |)([a-zA-Z_][a-zA-Z0-9_]*)')
RE_LIB_EXN = re.compile(r'exception ([a-zA-Z_][a-zA-Z0-9_]*)(?: of .+|)')

def handle_library(filename, library_name, soup):
    def anchor(id):
        return filename + '#' + id

    next_id = {'id': 0}
    def autoid():
        id, next_id['id'] = next_id['id'], next_id['id'] + 1
        return f'autoid_{id:04x}'
    def getid(element):
        if 'id' not in element.attrs:
            element['id'] = autoid()
            soup.made_changes = True
        return element['id']

    for pre in soup.find_all('pre'):
        pretext = ' '.join(pre.stripped_strings)
        m_type = RE_LIB_TYPE.fullmatch(pretext)
        if m_type is not None:
            typname = m_type.group(1)
            add_index(typname, TYPE_TYPE, anchor(getid(pre)))
            pre.insert_before(anchor_element(soup, TYPE_TYPE, typname))
            continue

        m_exn = RE_LIB_EXN.fullmatch(pretext)
        if m_exn is not None:
            exnname = m_exn.group(1)
            add_index(exnname, TYPE_EXCEPTION, anchor(getid(pre)))
            pre.insert_before(anchor_element(soup, TYPE_EXCEPTION, exnname))
            continue

def handle_module(filename, module_name, soup):
    def anchor(id):
        return filename + '#' + id

    for span in soup.find_all('span', id=True):
        spanid = span['id']
        if spanid.startswith('TYPEELT'):
            name = spanid[7:]
            # this can either be a constructor or a record field
            # full_code = ' '.join(span.parent.stripped_strings)
            if name.split('.')[-1][0].islower():
                typ = TYPE_FIELD
            else:
                typ = TYPE_CONSTRUCTOR
            add_index(f'{module_name}.{name}', typ, anchor(spanid))
            span.parent.insert_before(anchor_element(soup, typ, name))

        elif spanid.startswith('TYPE'):
            name = spanid[4:]
            span.parent.insert_before(anchor_element(soup, TYPE_TYPE, name))
            add_index(f'{module_name}.{name}', TYPE_TYPE, anchor(spanid))
            # add_index(f'{module_name}.{name}', TYPE_TYPE, anchor(f'//apple_ref/cpp/{TYPE_TYPE}/{name}'))
        elif spanid.startswith('EXCEPTION'):
            name = spanid[9:]
            add_index(f'{module_name}.{name}', TYPE_EXCEPTION, anchor(spanid))
            span.parent.insert_before(anchor_element(soup, TYPE_EXCEPTION, name))
        elif spanid.startswith('VAL'):
            name = spanid[3:]
            if contains(span.parent, '->'):
                valtype = TYPE_FUNCTION
            else:
                valtype = TYPE_VALUE
            add_index(f'{module_name}.{name}', valtype, anchor(spanid))
            span.parent.insert_before(anchor_element(soup, valtype, name))
            # print(list(span.parent.strings))

if __name__ == '__main__':
    import glob
    import shutil
    import sys
    import traceback

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    files = glob.glob(input_dir + '/**/*.html', recursive=True)
    # Ignore files related to the compiler's own library.
    # "Warning: This library is part of the internal OCaml compiler API, and is not the language standard library."
    files = [f for f in files if not fnmatch(f, "**/compilerlibref/*")]

    db_filename = os.path.join(output_dir, 'docSet.dsidx')

    if os.path.isfile(db_filename):
        os.unlink(db_filename)
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute('''CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)''')
    c.execute('''CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)''')
    conn.commit()

    for filename in files:
        relname = os.path.relpath(filename, start=input_dir)
        try:
            output_filename = os.path.join(output_dir, 'Documents', relname)
            if not os.path.isdir(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            doc, entries = run(relname, filename)
            if doc is not None and doc.made_changes:
                with open(output_filename, 'w') as f:
                    f.write(str(doc))
            else:
                # No need to copy, this has already been taken care of by make
                # shutil.copy(filename, output_filename)
                pass
        except:
            traceback.print_exc()
