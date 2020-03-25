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
        LIMIT 200
    ''', (ulang,)).fetchall()

    rv = OrderedDict()
    for result in results:
        if result['cor'] not in rv:
            rv[result['cor']] = []
        rv[result['cor']].append(result)

    return rv


def query_article(ulang, aname):
    db = get_db()
    translations = db.execute('''
        SELECT id, lang, atype, aname, title FROM
            articles
        WHERE
            aname = ?
        ORDER BY lang ASC
    ''', (aname,)).fetchall()

    results = db.execute('''
        SELECT id, aname, atype, title, source, authors, pubdate, cor, lead, content FROM
            articles
        WHERE
            lang = ? AND aname = ?
        ORDER BY pubdate DESC
    ''', (ulang, aname)).fetchall()

    return {
        "id": results[0]['id'],
        "lang": results[0]['lang'],
        "atype": results[0]['atype'],
        "aname": results[0]['aname'],
        "title": results[0]['title'],
        "source": results[0]['source'],
        "authors": results[0]['authors'],
        "pubdate": results[0]['pubdate'],
        "cor": results[0]['cor'],
        "lead": results[0]['lead'],
        "content": results[0]['content'],
        "translations": translations
    }
