#!/usr/bin/env python3

import sqlite3

def getall(filename):
    db = sqlite3.connect(f'file:{filename}?mode=ro', uri=True)
    c = db.cursor()
    c.execute('SELECT name, type, path FROM searchIndex')
    result = c.fetchall()
    db.close()
    return result


def run(orig_fn, new_fn):
    orig_rows = getall(orig_fn)
    new_rows = getall(new_fn)

    ref = {}

    for row in orig_rows:
        ref[row[0]] = row[1:]

    orig_names = set(x[0] for x in orig_rows)
    new_names = set(x[0] for x in new_rows)

    missing = orig_names - new_names

    for row in sorted(missing):
        print(f'missing: {row:15s} -> {ref[row]}')

if __name__ == '__main__':
    import sys
    run(sys.argv[1], sys.argv[2])
