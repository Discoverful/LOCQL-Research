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

en_uris_file = open('data/en_uris.txt', 'r')
en_questions_file = open('data/en_questions.txt', 'r')

PLACEMAKER_DOCLEN_LIMIT = 50000

local_uris_file = open('data/local_uris.txt', 'w')
local_questions_file = open('data/local_questions.txt', 'w')
while True:
    question_bundle = en_questions_file.readlines(int(PLACEMAKER_DOCLEN_LIMIT*0.9))
    if len(question_bundle) <= 0:
        break
    question_chunk = ''.join(question_bundle)
    assert len(question_chunk) < PLACEMAKER_DOCLEN_LIMIT
    params = urllib.urlencode({
    	'appid': appid,
        'documentType': 'text/plain',
    	'documentContent': question_chunk
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
    assert placemaker_xml is not None
    placemaker_etree = etree.parse(placemaker_xml)
    placemaker_xml.close()
    references = placemaker_etree.find(ns+'document/'+ns+'referenceList')
    reference_dict = {}
    for ref in references:
        start = int(ref.findtext(ns+'start'))
        end = int(ref.findtext(ns+'end'))
        assert (0 <= start) and (start < end) and (end <= len(question_chunk))
        reference_dict[start] = end - start  # length of place name
    i = 0  # word position index
    for question in question_bundle:
        uri = en_uris_file.readline().strip()
        question = question.decode('utf-8')
        local = False
        for j in range(len(question)):
            if (i+j) in reference_dict:
                l = reference_dict[i+j]
                placename = question[j:j+l]
                location = "%s\t[%d,%d]\t%s" % (uri, j, j+l, placename)
                print location.encode('utf-8')
                local = True
        if local:
            local_uris_file.write("%s\n" % uri)
            local_questions_file.write(question.encode('utf-8'))
        i += len(question)
    sleep(0.02)
local_uris_file.close()
local_questions_file.close()

en_uris_file.close()
en_questions_file.close()
