#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: dell
"""

from lxml import etree

# data_file = open('data/small_sample.xml')
data_file = open('data/FullOct2007.xml')

en_uris_file = open('data/en_uris.txt', 'w')
en_questions_file = open('data/en_questions.txt', 'w')
for event, element in etree.iterparse(data_file, tag='vespaadd'):
    # print etree.tostring(element, pretty_print=True)
    qlang = element.findtext('document/qlang')
    if qlang == 'en':
        uri = element.findtext('document/uri')
        question = element.findtext('document/subject').strip()
        question = question.replace('\t', ' ').replace('\n', ' ')
        en_uris_file.write("%s\n" % uri)
        en_questions_file.write("%s\n" % question.encode('utf-8'))
    element.clear()
en_uris_file.close()
en_questions_file.close()

data_file.close()
