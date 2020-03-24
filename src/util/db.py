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

docpath = os.path.join(find_path(), '../covid2019-memories')


def setup_db():
    conn = sqlite3.connect('data/memories.db')
    conn.execute('''DROP TABLE articles''')
    conn.execute('''
        CREATE TABLE articles (
                aid text,
                type text,
                cor text,
                lang text,
                pubdate text,
                source text,
                via text,
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
    conn = sqlite3.connect('data/memories.db')
    cor, pubdate, content = None, None, None
    for root, dirs, files in os.walk(docpath, followlinks=True):
        logger.info("db checking [%s, %s, %s] ..." % (root, str(dirs), str(files)))
        bname = path.basename(root)
        if bname in iso3166.entities.keys():
            cor = bname
        elif dc.is_date(bname):
            pubdate = bname
        else:
            for fnm in files:
                fpth = os.path.join(root, fnm)
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
                        source = meta['source'].strip()
                        via = meta['via'].strip()
                        title = meta['title'].strip()
                        authors = meta['authors'].strip()
                        proofreader = meta['proofreader'].strip()
                        photographer = meta['photographer'].strip()
                        leading = meta['leading'].strip()
                        if content is not None:
                            content = md.markdown(content)
                        else:
                            conn.execute('''
                                INSERT INTO articles VALUES (
                                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                                )''' % (
                                aid, type, cor, lang, pubdate, source, via,
                                title, authors, proofreader, photographer,
                                leading, content
                            ))

                        logger.info("inserting article [%s:%s] ... done" % (lang, aid))
                    except Exception as e:
                        logger.error(e)
    conn.commit()
    conn.close()

