# -*- coding: utf-8 -*-

from datetime import datetime


def parse_date(astring):
    try:
        return datetime.fromisoformat(astring)
    except Exception:
        return None
