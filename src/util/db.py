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

conn = sqlite3.connect('memories.db')

logger = logging.getLogger('db')

docpath = path.abspath(path.join(find_path(), '../covid2019-memories'))


def setup_db():
    conn = sqlite3.connect('data/memories.db')
    try:
        conn.execute('''DROP TABLE articles''')
    except Exception:
        pass

    conn.execute('''
        CREATE TABLE articles (
                aid text,
                type text,
                cor text,
                lang text,
                pubdate text,
                source text,
                via text,
                link text, 
                archive text, 
                snapshot text,
                title text,
                authors text,
                proofreader text,
                photographer text,
                leading text,
                content text
                )''')
    conn.commit()
    conn.close()


def init_db():
    leading, content = None, None
    conn = sqlite3.connect('data/memories.db')
    for root, dirs, files in os.walk(docpath, followlinks=True):
        bname = path.basename(root)

        hidden = False
        for p in path.normpath(root).split(os.sep):
            hidden = hidden or len(p) > 0 and p[0] == '.'
        for p in dirs:
            hidden = hidden or p[0] == '.'

        if not hidden:
            logger.info("db checking [%s, %s, %s] ..." % (root, str(dirs), str(files)))
            if bname in iso3166.entities.keys():
                cor = bname
            elif dc.parse_date(bname):
                pubdate = bname

            for fnm in files:
                fpth = path.join(root, fnm)

                if cor and pubdate and path.basename(fnm)[0] != '.':
                    aid, type, lang, ext = fnm.split('.')
                    logger.info("inserting article [%s:%s] ..." % (lang, aid))
                    with codecs.open(fpth, "r", "utf-8") as f:
                        parts = f.read().split('-------------')
                        if len(parts) == 1:
                            metatxt = parts[0]
                        else:
                            content = parts[0]
                            metatxt = parts[1]

                        try:
                            meta = load_yaml(metatxt)
                            source = meta['source'] or ''
                            via = meta['via'] or ''
                            link = meta['link'] or ''
                            archive = meta['archive'] or ''
                            snapshot = meta['snapshot'] or ''
                            title = meta['title'] or ''
                            authors = meta['authors'] or ''
                            proofreader = meta['proofreader'] or ''
                            photographer = meta['photographer'] or ''
                            leading = meta['leading'] or ''
                            if content is not None:
                                content = md.markdown(content)

                            conn.execute('INSERT INTO articles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                                    aid, type, cor, lang, pubdate, source, via, link, archive, snapshot,
                                    title, authors, proofreader, photographer,
                                    leading, content
                            ))

                            logger.info("inserting article [%s:%s] ... done" % (lang, aid))
                        except Exception as e:
                            logger.error(e)
    conn.commit()
    conn.close()


setup_db()
init_db()


def query_article(ulang, aid):
    return None
