#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

local_uris_file = open('data/local_uris.txt', 'r')
local_uris_dict = {}.fromkeys([line.strip() for line in local_uris_file], True) 
local_uris_file.close()

from lxml import etree
from datetime import datetime

# data_file = open('data/small_sample.xml')
data_file = open('data/FullOct2007.xml')

local_uris_list = []
local_questions_dict = {}
local_categories_dict = {}
local_dates_dict = {}
for event, element in etree.iterparse(data_file, tag='vespaadd'):
    # print etree.tostring(element, pretty_print=True)
    qlang = element.findtext('document/qlang')
    if qlang == 'en':
        uri = element.findtext('document/uri')
        if uri in local_uris_dict:
            local_uris_list.append(uri)
            #
            question = element.findtext('document/subject').strip()
            question = question.replace('\t', ' ').replace('\n', ' ')
            local_questions_dict[uri] = question.encode('utf-8')
            #
            maincat = element.findtext('document/maincat')
            subcat = element.findtext('document/subcat')
            cat = element.findtext('document/cat')
            categories = ''
            if cat:
                assert maincat and subcat
                categories = maincat + '/' + subcat
                if cat != subcat:
                    categories += '/' + cat
                categories = categories.replace(' ', '_')
            local_categories_dict[uri] = categories.encode('utf-8')
            #
            date = datetime.fromtimestamp(int(element.findtext('document/date')))
            local_dates_dict[uri] = date
    element.clear()

data_file.close()

import cPickle as pickle

local_uris_pkl = open('data/local_uris.pkl', 'wb')
pickle.dump(local_uris_list, local_uris_pkl)
local_uris_pkl.close()

local_questions_pkl = open('data/local_questions.pkl', 'wb')
pickle.dump(local_questions_dict, local_questions_pkl)
local_questions_pkl.close()

local_categories_pkl = open('data/local_categories.pkl', 'wb')
pickle.dump(local_categories_dict, local_categories_pkl)
local_categories_pkl.close()

local_dates_pkl = open('data/local_dates.pkl', 'wb')
pickle.dump(local_dates_dict, local_dates_pkl)
local_dates_pkl.close()
