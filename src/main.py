# -*- coding: utf-8 -*-

import app as webapp
import util.i18n as i18n

from itertools import product
from flask import url_for


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


def build_site():
    appclient = client()

    langs = get_languages()
    persps = get_perspectives()
    cats = get_categories()

    for lang, persp, cat in product(langs, persps, cats):
        days = get_days(persp)
        for day in days:
            with webapp.app.app_context():
                url = url_for('index', ulang=lang, perspective=persp, category=cat, day=day)
                rv = appclient.get(url)
                print(url)


if __name__ == '__main__':
    build_site()
