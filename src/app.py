# -*- coding: utf-8 -*-

import logging

from flask import Flask, render_template
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy

import util.i18n as i18n
import util.basepath as find_path
import util.query as q




app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/data/memories.db' % find_path()
db = SQLAlchemy(app)

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


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(10), unique=False, nullable=False)
    atype = db.Column(db.String(1), unique=False, nullable=False)
    aname = db.Column(db.String(10), unique=False, nullable=False)
    lang = db.Column(db.String(10), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username



def build_context(ulang):
    default_cor = ['cn', 'it']
    rv = q.query_index(ulang)

    return {
        'ulang': ulang,

        'languages': i18n.tables['languages'],
        'categories': i18n.table(ulang, 'category'),
        'lables': i18n.table(ulang, 'lable_index_page'),
        'corz': i18n.table(ulang, 'country_or_region'),
        'perspectives': i18n.table(ulang, 'perspective'),

        'default_cor': default_cor,
        'results': rv,
    }


def render_index(ulang='en', perspective='da', category='_', day='latest'):
    return render_template('index.html', **build_context(ulang))


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


@app.route('/<ulang>/index.html')
def index(ulang='en'):
    return render_index(ulang=ulang)


@app.route('/<ulang>/<pubdate>/<aname>.html')
def article(ulang, pubdate, aname):
    default_cor = ['cn', 'it']
    a = q.query_article(ulang, pubdate, aname)

    return render_template('article.html', **{
        "article": a,
        'ulang': ulang,
        'pubdate': pubdate,
        'name': aname,

        'languages': i18n.tables['languages'],
        'categories': i18n.table(ulang, 'category'),
        'lables': i18n.table(ulang, 'lable_index_page'),
        'corz': i18n.table(ulang, 'country_or_region'),
        'perspectives': i18n.table(ulang, 'perspective'),

        'default_cor': default_cor,
    })

