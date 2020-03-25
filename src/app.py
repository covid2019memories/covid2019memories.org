# -*- coding: utf-8 -*-

import logging

from flask import Flask, render_template
from logging.config import dictConfig

import util.i18n as i18n
import util.db as db
import util.query as q


app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')
db.init_app(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


def build_context(ulang, perspective, category, day):
    default_cor = ['cn', 'it']
    rv = q.query_index(ulang, perspective, category, day)

    return {
        'ulang': ulang,
        'perspective': perspective,
        'category': category,
        'day': day,

        'languages': i18n.tables['languages'],
        'categories': i18n.table(ulang, 'category'),
        'lables': i18n.table(ulang, 'lable_index_page'),
        'corz': i18n.table(ulang, 'country_or_region'),
        'perspectives': i18n.table(ulang, 'perspective'),

        'default_cor': default_cor,
        'results': rv,
    }


def render_index(ulang='en', perspective='da', category='_', day='latest'):
    return render_template('index.html', **build_context(ulang, perspective, category, day))


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/index.html')
def home():
    return render_index()


@app.route('/<ulang>/index/<perspective>/<category>/<day>.html')
def index(ulang='en', perspective='datealigned', category='_', day='latest'):
    return render_index(ulang=ulang, perspective=perspective, category=category, day=day)


@app.route('/<ulang>/post/<aid>.html')
def post(ulang, aid):
    article = db.query_article(ulang, type, aid)
    return render_template('post.html')


@app.route('/<ulang>/translation/<tid>')
def translation():
    return render_template('translation.html')
