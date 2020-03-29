# -*- coding: utf-8 -*-

from collections import OrderedDict

from util.db import get_db


def query_index(ulang):
    db = get_db()
    results = db.execute('''
        SELECT id, aname, atype, title, source, authors, pubdate, cor, lead, cover FROM
            articles
        WHERE
            lang = ?
        ORDER BY pubdate DESC
        LIMIT 1000
    ''', (ulang,)).fetchall()

    rv = OrderedDict()
    for result in results:
        if result['cor'] not in rv:
            rv[result['cor']] = []
        rv[result['cor']].append(result)

    return rv


def query_article(ulang, pubdate, aname):
    db = get_db()
    translations = db.execute('''
        SELECT id, lang, atype, aname, title FROM
            articles
        WHERE
            aname = ? and pubdate = ?
        ORDER BY lang ASC
    ''', (aname, pubdate)).fetchall()

    results = db.execute('''
        SELECT id, lang, atype, aname, title, source, authors, pubdate, cor, lead, content FROM
            articles
        WHERE
            lang = ? AND aname = ? and pubdate = ?
        ORDER BY pubdate DESC
    ''', (ulang, aname, pubdate)).fetchall()

    return {
        "id": results[0][0],
        "lang": results[0][1],
        "atype": results[0][2],
        "aname": results[0][3],
        "title": results[0][4],
        "source": results[0][5],
        "authors": results[0][6],
        "pubdate": results[0][7],
        "cor": results[0][8],
        "lead": results[0][9],
        "content": results[0][10],
        "translations": [{ "lang": t[1], "atype": t[2], "aname": t[3], "title": t[4] } for t in translations]
    }
