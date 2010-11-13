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
    if (question.lower().find(place) >= 0):
        question = question[0].upper() + question[1:]
        question = question.replace("I'm ", "I am ")
        question = question.replace("What's ", "What is ")
        question = question.replace("Whats ", "What is ")
        question = question.replace("Where's ", "Where is ")
        question = question.replace("Wheres ", "Where is ")
        question = question.replace("Which's ", "Where is ")
        question = question.replace("Whichs ", "Where is ")
        print question
