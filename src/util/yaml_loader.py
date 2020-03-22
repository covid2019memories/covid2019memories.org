# -*- coding: utf-8 -*-

import yaml


def load_yaml(s):
    if yaml.__with_libyaml__:
        return yaml.load(s, Loader=yaml.CLoader)
    else:
        return yaml.load(s)
