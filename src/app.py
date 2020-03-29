# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import util.i18n as i18n
import util.db as d

from util.basepath import find_path

app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/data/memories.db' % find_path()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(10), unique=False, nullable=False)
    atype = db.Column(db.String(2), unique=False, nullable=False)
    aname = db.Column(db.String(100), unique=False, nullable=False)
    cor = db.Column(db.String(10), unique=False, nullable=False)
    pubdate = db.Column(db.String(10), unique=False, nullable=False)
    source = db.Column(db.String(100), unique=False, nullable=False)
    via = db.Column(db.String(150), unique=False, nullable=False)
    link = db.Column(db.String(150), unique=False, nullable=False)
    archive = db.Column(db.String(150), unique=False, nullable=False)
    snapshot = db.Column(db.String(150), unique=False, nullable=False)
    title = db.Column(db.String(200), unique=False, nullable=False)
    authors = db.Column(db.String(200), unique=False, nullable=False)
    proofreader = db.Column(db.String(200), unique=False, nullable=False)
    photographer = db.Column(db.String(200), unique=False, nullable=False)
    lead = db.Column(db.Text, unique=False, nullable=False)
    content = db.Column(db.Text, unique=False, nullable=False)
    cover = db.Column(db.Text, unique=False, nullable=False)

    cnstr = db.UniqueConstraint(lang, atype, pubdate, aname, name='uix')

    def __repr__(self):
        return '<Article %s %s %s %s>' % (self.lang, self.atype, self.pubdate, self.aname)


db.Index('idx_articles_pn', Article.pubdate.name, Article.aname.name)
db.Index('idx_articles_pc', Article.pubdate.name, Article.cor.name)
db.Index('idx_articles_c', Article.cor.name)

db.drop_all()
db.create_all()
d.init_db(db, Article)


def build_context(ulang):
    default_cor = ['cn', 'it']
    results = Article.query.filter_by(lang=ulang).order_by(Article.pubdate.desc())

    rv = OrderedDict()
    for result in results:
        if result.cor not in rv:
            rv[result.cor] = []
        rv[result.cor].append(result)

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


@app.route('/<ulang>/<pubdate>/<aname>.<atype>.html')
def article(ulang, pubdate, aname, atype):
    default_cor = ['cn', 'it']
    a = Article.query.filter_by(lang=ulang, atype=atype, pubdate=pubdate, aname=aname).first()

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

