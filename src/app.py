# -*- coding: utf-8 -*-

from flask import Flask, escape, request, render_template

import util.i18n as i18n

app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')


def build_context(ulang, perspective, category, day):
    return {
        'ulang': ulang,
        'perspective': perspective,
        'languages': i18n.tables['languages'],
        'categories': i18n.table(ulang, 'category'),
        'category': category,
        'day': day
    }


def render_index(ulang='en', perspective='datealigned', category='_', day='latest'):
    return render_template('index.html', **build_context(ulang, perspective, category, day))


@app.route('/')
def home():
    return render_index()


@app.route('/<ulang>/index/<perspective>/<category>/<day>')
def index(ulang='en', perspective='datealigned', category='_', day='latest'):
    return render_index(ulang=ulang, perspective=perspective, category=category, day=day)


@app.route('/<ulang>/post/<pid>')
def post():
    return render_template('post.html')


@app.route('/<ulang>/translation/<tid>')
def translation():
    return render_template('translation.html')

