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
                id integer primary key asc,
                lang text not null,
                atype text not null,
                aname text not null,
                cor text not null,
                pubdate text not null,
                source text not null,
                via text,
                link text,
                archive text,
                snapshot text,
                title text,
                authors text,
                proofreader text,
                photographer text,
                lead text not null,
                content text not null
    )''')

    conn.execute("CREATE UNIQUE INDEX idx_articles_ltn ON articles(lang, atype, aname)")
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

            if not hidden:
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
                            parts = f.read().split('-------------')
                            if len(parts) == 1:
                                metatxt = parts[0]
                            else:
                                content = parts[0]
                                metatxt = parts[1]

                            tmp = ''
                            metatxt, lead = metatxt.split('lead:')
                            for line in metatxt.split('\n'):
                                flds = line.split(': ')
                                if len(flds) == 2:
                                    tmp = '%s\n%s: %s' % (tmp, flds[0], flds[1])
                                elif len(flds) > 2:
                                    tmp = '%s\n%s: "%s"' % (tmp, flds[0], '\: '.join(flds[1:]))
                                else:
                                    raise Exception(flds[0])

                            lead = lead.replace('\n  ', ' ')
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
                                if content is not None:
                                    content = md.markdown(content)

                                conn.execute('''
                                    INSERT INTO articles(
                                        aname, atype, cor, lang, pubdate, source, via, link, archive, snapshot,
                                        title, authors, proofreader, photographer,
                                        lead, content
                                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                                        aname, atype, cor, lang, pubdate, source, via, link, archive, snapshot,
                                        title, authors, proofreader, photographer,
                                        lead, content
                                ))
                                conn.commit()
                                logger.info("inserting article [%s:%s] ... done" % (lang, aname))
                            except Exception as e:
                                logger.error(e)

setup_db()
init_db()


def query_article(ulang, type, aid):
    return None
