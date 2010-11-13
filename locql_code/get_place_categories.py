#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

import cPickle as pickle

local_uris_pkl = open('data/local_uris.pkl', 'rb')
local_uris_list = pickle.load(local_uris_pkl)
local_uris_pkl.close()

local_questions_pkl = open('data/local_questions.pkl', 'rb')
local_questions_dict = pickle.load(local_questions_pkl)
local_questions_pkl.close()

local_categories_pkl = open('data/local_categories.pkl', 'rb')
local_categories_dict = pickle.load(local_categories_pkl)
local_categories_pkl.close()

import sys

place = ''
if len(sys.argv) > 1:
    place = sys.argv[1].lower()

for uri in local_uris_list:
    question = local_questions_dict[uri]
    categories = local_categories_dict[uri]
    if (not categories) or (categories.find('Yahoo!') >= 0):
        continue
    if (question.lower().find(place) >= 0):
        cat_path = categories.split('/')
        if cat_path[-1].find('Other_') == 0:
            categories = '/'.join(cat_path[:-1])
        categories = categories.replace('_&_', '-and-')
        categories = categories.replace('_-_', '-')
        categories = categories.replace(',', '').replace('+', '')
        categories = categories.replace('(', '').replace(')', '')
        categories = categories.replace('_', '-')
        categories = categories.replace('/', ' ')
        print categories
