# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import absolute_import

import codecs
import logging
import os
import os.path as path
import markdown as md

import util.iso3166 as iso3166
import util.datecalc as dc

from util.basepath import find_path
from util.yaml_loader import load_yaml

logger = logging.getLogger('werkzeug')

docpath = path.abspath(path.join(find_path(), '../covid2019-memories'))

dedup = {}


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


def init_db(db, article_cls):
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
                    key = "%s:%s:%s:%s" % (lang, atype, pubdate, aname)
                    if key not in dedup:
                        dedup[key] = True
                        logger.info("inserting article [%s:%s:%s:%s] ..." % (lang, atype, pubdate, aname))
                        with codecs.open(fpth, "r", "utf-8") as f:
                            content, metatxt = parse(f.read())
                            try:
                                db.session.flush()
                                article = article_cls()
                                meta = load_yaml(metatxt)

                                article.lang = lang
                                article.atype = atype
                                article.aname = aname
                                article.pubdate = pubdate
                                article.cor = cor
                                article.source = meta['source'] or '_'
                                article.via = meta['via'] or '_'
                                article.link = meta['link'] or '_'
                                article.archive = meta['archive'] or '_'
                                article.snapshot = meta['snapshot'] or '_'
                                article.title = meta['title'] or '_'
                                article.authors = meta['authors'] or '_'
                                article.proofreader = meta['proofreader'] or '_'
                                article.photographer = meta['photographer'] or '_'
                                article.lead = meta['lead'] or '_'
                                article.cover = meta['cover'] or '_'
                                if content is not None:
                                    article.content = md.markdown(content)

                                article.title = article.title.replace('::', ':')
                                article.title = article.title.replace('#', '')
                                article.title = article.title.replace('*', '')
                                article.title = article.title.replace('[', '')
                                article.title = article.title.replace(']', '')

                                db.session.add(article)
                                logger.info("%s %s %s %s %s", atype, cor, lang, pubdate, aname)
                                db.session.commit()
                                logger.info("inserting article [%s:%s] ... done" % (lang, aname))
                                db.session.flush()

                                for h in logger.handlers:
                                    h.flush()
                            except Exception as e:
                                db.session.rollback()
                                db.session.flush()

                                logger.error(e)
                                for h in logger.handlers:
                                    h.flush()
