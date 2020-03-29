# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import absolute_import

import codecs
import logging
import os
import os.path as path
import sqlite3
import markdown as md

import util.iso3166 as iso3166
import util.datecalc as dc


from util.basepath import find_path
from util.yaml_loader import load_yaml

logger = logging.getLogger('werkzeug')

docpath = path.abspath(path.join(find_path(), '../covid2019-memories'))


def g():
    from flask import g as ctx
    return ctx


def escape(s):
    s = '%s' % s
    if s is None or s == '':
        return '_'

    if s[0] == "'" and s[-1] == "'":
        s = s[1:-1]
    if s[0] == '"' and s[-1] == '"':
        s = s[1:-1]

    return s.replace('"', '\\"')


def normalize(metatxt):
    tmp = ''
    for line in metatxt.split('\n'):
        flds = line.split(': ')
        if len(flds) == 2:
            tmp = '%s\n%s: "%s"' % (tmp, flds[0], escape(flds[1]))
        elif len(flds) > 2:
            tmp = '%s\n%s: "%s"' % (tmp, flds[0], escape(':: '.join(flds[1:])))
        else:
            if flds[0]:
                tmp = '%s\n%s: _' % (tmp, flds[0])
    return tmp


def parse(text):
    parts = text.split('-------------')
    return '-------------'.join(parts[0:-1]), normalize(parts[-1])


def setup_db():
    conn = sqlite3.connect('data/memories.db')
    try:
        conn.execute('''DROP TABLE articles''')
    except Exception:
        pass

    conn.execute('''
        CREATE TABLE articles (
                id integer primary key asc,
                lang text not null,
                atype text not null,
                aname text not null,
                cor text not null,
                pubdate text not null,
                source text not null,
                via text default '',
                link text default '',
                archive text default '',
                snapshot text default '',
                title text default '',
                authors text default '',
                proofreader text default '',
                photographer text default '',
                lead text not null,
                content text not null,
                cover text not null
    )''')

    conn.execute("CREATE UNIQUE INDEX idx_articles_ltn ON articles(lang, pubdate, atype, aname)")
    conn.execute("CREATE INDEX idx_articles_n ON articles(aname)")
    conn.execute("CREATE INDEX idx_articles_ltcp ON articles(lang, atype, cor, pubdate)")

    conn.commit()
    conn.close()


def init_db():
    with sqlite3.connect('data/memories.db') as conn:
        for root, dirs, files in os.walk(docpath, followlinks=True):
            bname = path.basename(root)

            hidden = False
            for p in path.normpath(root).split(os.sep):
                hidden = hidden or len(p) > 0 and p[0] == '.'
            for p in dirs:
                hidden = hidden or p[0] == '.'

            if not hidden and bname != 'memories':
                logger.info("db checking [%s, %s, %s] ..." % (root, str(dirs), str(files)))
                if bname in iso3166.entities.keys():
                    cor = bname
                elif dc.parse_date(bname):
                    pubdate = bname

                for fnm in files:
                    fpth = path.join(root, fnm)

                    if cor and pubdate and path.basename(fnm)[0] != '.':
                        aname, atype, lang, ext = fnm.split('.')
                        logger.info("inserting article [%s:%s] ..." % (lang, aname))
                        with codecs.open(fpth, "r", "utf-8") as f:
                            content, metatxt = parse(f.read())
                            try:
                                meta = load_yaml(metatxt)
                                source = meta['source'] or '_'
                                via = meta['via'] or '_'
                                link = meta['link'] or '_'
                                archive = meta['archive'] or '_'
                                snapshot = meta['snapshot'] or '_'
                                title = meta['title'] or '_'
                                authors = meta['authors'] or '_'
                                proofreader = meta['proofreader'] or '_'
                                photographer = meta['photographer'] or '_'
                                lead = meta['lead'] or '_'
                                cover = meta['cover'] or '_'
                                if content is not None:
                                    content = md.markdown(content)

                                title = title.replace('::', ':')

                                conn.execute('''
                                    INSERT INTO articles(
                                        aname, atype, cor, lang, pubdate, source, via, link, archive, snapshot,
                                        title, authors, proofreader, photographer,
                                        lead, content, cover
                                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                                        aname, atype, cor, lang, pubdate, source, via, link, archive, snapshot,
                                        title, authors, proofreader, photographer,
                                        lead, content, cover
                                ))
                                logger.info("%s %s %s %s %s", atype, cor, lang, pubdate, aname)
                                conn.commit()
                                logger.info("inserting article [%s:%s] ... done" % (lang, aname))

                                for h in logger.handlers:
                                    h.flush()
                            except Exception as e:
                                logger.error(e)
                                for h in logger.handlers:
                                    h.flush()


setup_db()
init_db()


def get_db():
    ctx = g()
    if 'db' not in ctx:
        ctx.db = sqlite3.connect(
            'data/memories.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        ctx.db.row_factory = sqlite3.Row

    return ctx.db


def close_db(e=None):
    db = g().pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
