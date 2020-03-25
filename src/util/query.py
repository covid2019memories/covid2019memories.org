# -*- coding: utf-8 -*-

from collections import OrderedDict

from util.db import get_db


def query_index(ulang, perspective, category, day):
    db = get_db()
    results = db.execute('''
        SELECT id, aname, atype, title, source, authors, pubdate, cor, lead FROM
            articles
        WHERE
            lang = ?
        ORDER BY pubdate DESC
    ''', (ulang,)).fetchall()

    rv = OrderedDict()
    for result in results:
        if result['cor'] not in rv:
            rv[result['cor']] = []
        rv[result['cor']].append(result)

    return rv
