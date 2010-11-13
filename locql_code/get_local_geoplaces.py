#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

import urllib, urllib2
from lxml import etree
from time import sleep

appid = 'wDfF6HTV34FDFZdlmVPot_dyFLn29fFSp3SXUBouVhXScU3T0pzhBR1JhCxhm7099A--'

url = 'http://wherein.yahooapis.com/v1/document'
ns = "{%s}" % 'http://wherein.yahooapis.com/v1/schema'

# Yahoo Placemaker has a daily usage limit of 50,000 requests
# Therefore the geo-parsing wrok has to be done incrementally
# Let's start from where it left offf
local_uris_file = open('data/local_uris.txt', 'r')
local_questions_file = open('data/local_questions.txt', 'r')
local_geoplaces_file = open('data/local_geoplaces.txt', 'r')
for geoplace in local_geoplaces_file:
    local_uris_file.readline()
    local_questions_file.readline()
local_geoplaces_file.close()

local_geoplaces_file = open('data/local_geoplaces.txt', 'a')
local_geoplaces_logs = open('data/local_geoplaces.log', 'a')
for question in local_questions_file:
    uri = local_uris_file.readline().strip()
    params = urllib.urlencode({
    	'appid': appid,
        'documentType': 'text/plain',
    	'documentContent': question
    })
    placemaker_xml = None
    for k in range(3):
        try:
            placemaker_xml = urllib2.urlopen(url, params)
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
            if e.code == 999:  # Unable to process request at this time
                break # Have to wait for 24 hours to run again
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason
        if placemaker_xml is not None:
            break
        else:
            sleep((k+1)*60)
    if placemaker_xml is None:
        break
    placemaker_etree = etree.parse(placemaker_xml)
    document = placemaker_etree.find(ns+'document')
    document_xml = ''
    if len(document) > 0:
        document_xml = etree.tostring(document).strip()
        document_xml = document_xml.replace('\t', ' ').replace('\n', ' ')
    local_geoplaces_file.write("%s\n" % document_xml)
    local_geoplaces_logs.write("%s\n" % uri)
    placemaker_xml.close()
    sleep(0.02);
local_geoplaces_file.close()
local_geoplaces_logs.close()

local_uris_file.close()
local_questions_file.close()
