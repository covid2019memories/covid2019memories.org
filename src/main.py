# -*- coding: utf-8 -*-

import os
import os.path as path
import pathlib
import re

import app as webapp
import util.i18n as i18n

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


def build_page(appclient, url, fpth=None):
    with webapp.app.app_context():
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

    langs = get_languages()
    persps = get_perspectives()
    cats = get_categories()
    for lang, persp, cat in product(langs, persps, cats):
        days = get_days(persp)
        for day in days:
            with webapp.app.test_request_context():
                url = url_for('index', ulang=lang, perspective=persp, category=cat, day=day)
                build_page(appclient, url)


if __name__ == '__main__':
    build_site()
