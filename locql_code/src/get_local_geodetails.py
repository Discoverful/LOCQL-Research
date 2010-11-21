#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

import cPickle as pickle

local_uris_pkl = open('data/local_uris.pkl', 'rb')
local_uris_list = pickle.load(local_uris_pkl)
local_uris_pkl.close()

local_geoplaces_file = open('data/local_geoplaces.txt')
local_geoplaces_list = [line.strip() for line in local_geoplaces_file]
local_geoplaces_file.close()

assert len(local_uris_list) == len(local_geoplaces_list)

from lxml import etree

ns = "{%s}" % 'http://wherein.yahooapis.com/v1/schema'

local_geodetails_file = open('data/local_geodetails.txt', 'w')
for uri, placemaker_xml in zip(local_uris_list, local_geoplaces_list):
    if placemaker_xml == '':
        continue
    placemaker_etree = etree.fromstring(placemaker_xml)
    if placemaker_etree is None:
        continue
    aS = placemaker_etree.find(ns+'administrativeScope')
    aS_type = aS.findtext(ns+'type')
    aS_name = aS.findtext(ns+'name').encode('utf-8')
    if aS_type != 'Undefined':
        local_geodetails_file.write("%s\t%s\t%s\n" % (uri, aS_type, aS_name))
local_geodetails_file.close()

