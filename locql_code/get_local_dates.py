#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

local_uris_dict = {}
local_uris_file = open('data/local_uris.txt', 'r')
for line in local_uris_file:
    uri = line.strip()
    local_uris_dict[uri] = True
local_uris_file.close()

from lxml import etree
from datetime import datetime

data_file = open('data/small_sample.xml')
# data_file = open('data/FullOct2007.xml')

local_dates_dict = {}
for event, element in etree.iterparse(data_file, tag='vespaadd'):
    # print etree.tostring(element, pretty_print=True)
    qlang = element.findtext('document/qlang')
    if qlang == 'en':
        uri = element.findtext('document/uri')
        if uri in local_uris_dict:
            date = datetime.fromtimestamp(int(element.findtext('document/date')))
            local_dates_dict[uri] = date
            print uri, str(date), date.weekday()
    element.clear()

data_file.close()

import cPickle as pickle
local_dates_pkl = open('data/local_dates.pkl', 'wb')
pickle.dump(local_dates_dict, local_dates_pkl)
local_dates_pkl.close()
