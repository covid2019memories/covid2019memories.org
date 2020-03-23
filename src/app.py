# -*- coding: utf-8 -*-

from flask import Flask, escape, request, render_template

import util.i18n as i18n

app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')


def render_index(ulang, perspective, languages, countries, categories, gourpby, time):
    return render_template('index.html', **{
        'ulang': ulang,
        'perspective': perspective,
        'languages': languages,
        'countries': countries,
        'categories': categories,
        'gourpby': gourpby,
        'time': time,
    })


@app.route('/')
def home():
    return render_index(**{
        'ulang': 'en',
        'perspective': 'datealigned',
        'languages': 'any',
        'countries': 'cn+kr+ja+it+ir',
        'categories': 'wrd+plt+bsn+spt+clt+tch+sci+hlt+opn+psn',
        'gourpby': 'country',
        'time': 20,
    })


@app.route('/<ulang>/index/<perspective>/<languages>/<countries>/<categories>/<gourpby>/<time>')
def index(ulang, perspective, languages, countries, categories, gourpby, time):
    return render_index(**{
        'ulang': ulang,
        'perspective': perspective,
        'languages': languages,
        'countries': countries,
        'categories': categories,
        'gourpby': gourpby,
        'time': time,
    })


@app.route('/<ulang>/post/<pid>')
def post():
    return render_template('post.html')


@app.route('/<ulang>/translation/<tid>')
def translation():
    return render_template('translation.html')

