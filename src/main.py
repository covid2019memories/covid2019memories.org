# -*- coding: utf-8 -*-

import os
import os.path as path
import pathlib
import re
import logging

import util.i18n as i18n

from pathlib import Path
from distutils.dir_util import copy_tree
from flask import url_for

from util.basepath import find_path


log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)
basepath = path.join(os.getcwd(), 'public')

pth = Path(find_path(), 'data/memories.db-journal')
if pth.exists():
    pth.unlink()
pth = Path(find_path(), 'data/memories.db')
if pth.exists():
    pth.unlink()
log.info('delete database files %s' % pth)


import app as webapp


def client():
    webapp.app.config['TESTING'] = True
    return webapp.app.test_client()


def get_languages():
    return i18n.tables['languages'].keys()


def build_page(appclient, url, fpth=None):
    print(url)
    rv = appclient.get(url)
    if rv.status == '200 OK':
        if fpth is None:
            fpth = '%s%s' % (basepath, url)
            pathlib.Path(fpth).parent.mkdir(parents=True, exist_ok=True)
        with open(fpth, mode='w') as f:
            body = rv.data.decode(encoding='UTF-8')
            body = re.sub(r'\s\s+', ' ', body)
            f.write(body)
    else:
        raise Exception()


def build_site():
    appclient = client()

    # Static resources
    copy_tree('static/', 'public/')

    # Home page
    build_page(appclient, '/index.html', fpth='%s%s' % (basepath, '/index.html'))

    # Skeleton index pages
    langs = get_languages()
    print(langs)
    for lang in langs:
        with webapp.app.test_request_context():
            url = url_for('index', ulang=lang)
            build_page(appclient, url)

    # Detailed article pages
    for lang in langs:
         with webapp.app.test_request_context():
            rv = webapp.query_articles(lang)
            for cor, results in rv.items():
                for result in results:
                    pubdate = result.pubdate
                    aname = result.aname
                    atype = result.atype
                    url = url_for('article', ulang=lang, pubdate=pubdate, atype=atype, aname=aname)
                    build_page(appclient, url)


if __name__ == '__main__':
    with webapp.app.app_context():
        build_site()
