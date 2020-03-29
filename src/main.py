# -*- coding: utf-8 -*-

import os
import os.path as path
import pathlib
import re

import app as webapp
import util.i18n as i18n
import util.query as q

from distutils.dir_util import copy_tree
from itertools import product
from flask import url_for


basepath = path.join(os.getcwd(), 'public')


def client():
    webapp.app.config['TESTING'] = True
    return webapp.app.test_client()


def get_languages():
    return i18n.tables['languages'].keys()


def get_perspectives():
    return i18n.table('en', 'perspective').keys()


def get_categories():
    return ['_'] + list(i18n.table('en', 'category').keys())


def get_days(perspective):
    return ['latest']


def get_dates():
    return [
        '2019-12-31',
        '2020-01-06', '2020-01-19', '2020-01-20', '2020-01-21', '2020-01-22', '2020-01-23', '2020-01-24',
        '2020-01-25', '2020-01-26',
    ]


def build_page(appclient, url, fpth=None):
    url = re.sub('[^0-9a-zA-Z-\./]+', '', url)
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
    langs = get_languages()
    for lang in product(langs):
         with webapp.app.test_request_context():
            results = q.query_index(ulang=lang)
            for result in results:
                pubdate = result['pubdate']
                aname = result['aname']
                pubdate = re.sub('[^0-9a-zA-Z-\./]+', '', pubdate)
                aname = re.sub('[^0-9a-zA-Z-\./]+', '', aname)
                url = url_for('article', ulang=lang, pubdate=pubdate, aname=aname)
                build_page(appclient, url)


if __name__ == '__main__':
    with webapp.app.app_context():
        build_site()
