# -*- coding: utf-8 -*-

from datetime import datetime


def parse_date(astring):
    return datetime.fromisoformat(astring)
