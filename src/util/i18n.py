# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import codecs
import logging
import os
import os.path as path

from contextlib import contextmanager
from os import getcwd

from util.yaml_loader import load_yaml


def find_path():
    cwd = getcwd()
    venvpath = os.path.join(cwd, '.py')

    if os.path.exists(venvpath):
        basepath = cwd
    else:
        testpath = os.path.join(os.path.dirname(__file__), '..')
        level = 0
        while level < 6:
            testpath = os.path.join(testpath, '..')
            venvpath = os.path.join(testpath, '.py')
            if os.path.exists(venvpath):
                basepath = testpath
                break
            level += 1
        else:
            basepath = cwd

    return basepath


logger = logging.getLogger('i18n')

i18n_path = os.path.join(find_path(), 'i18n')

tables = {}


for root, dirs, files in os.walk(i18n_path, followlinks=True):
    logger.info("i18n checking [%s, %s, %s] ..." % (root, str(dirs), str(files)))
    if path.basename(root) == 'i18n':
        for d in dirs:
            tables[d] = {}
    else:
        lang = path.basename(root)
        logger.info("initialing language %s ..." % lang)

        for fnm in files:
            fpth = os.path.join(root, fnm)
            bndl = ''.join(fnm.split('.')[:-1])
            logger.info("initialing bundle [%s:%s] ..." % (lang, bndl))
            with codecs.open(fpth, "r", "utf-8") as f:
                s = f.read()
                try:
                    tables[lang][bndl] = load_yaml(s)
                    logger.info("init bundle [%s:%s] done ..." % (lang, bndl))
                except Exception as e:
                    tables[lang][bndl] = {}
                    logger.error(e)


def table(lang, tname):
    if lang in tables and tname in tables[lang]:
        return tables[lang][tname]
    else:
        #logger.warn('[%s:%s] is not supported, using en_US by default!' % (lang, tname))
        return tables['en_US'][tname]


def get(lang, table, key):
    if lang in tables and table in tables[lang] and key in tables[lang][table]:
        return tables[lang][table][key]
    else:
        #logger.warn('[%s:%s:%s] is not supported, using en_US by default!' % (lang, table, key))
        return tables['en_US'][table][key]


@contextmanager
def ctx(lang, tname):
    yield table(lang, tname)
