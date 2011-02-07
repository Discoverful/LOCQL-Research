import urllib, urllib2
from xml.etree import ElementTree as ET

appid = 'wDfF6HTV34FDFZdlmVPot_dyFLn29fFSp3SXUBouVhXScU3T0pzhBR1JhCxhm7099A--'

url = 'http://wherein.yahooapis.com/v1/document'
ns = "{%s}" % 'http://wherein.yahooapis.com/v1/schema'

def geoparsing(text):
    if not text:
        return ''
    params = urllib.urlencode({
    	'appid': appid,
        'documentType': 'text/plain',
    	'documentContent': text.encode('utf-8')
    })
    placemaker_xml = urllib2.urlopen(url, params)
    if not placemaker_xml:
        return text
    placemaker_etree = ET.parse(placemaker_xml)
    placemaker_xml.close()
    references = placemaker_etree.find(ns+'document/'+ns+'referenceList')
    if not references:
        return text
    place_segments = []
    for ref in references:
        start = int(ref.findtext(ns+'start'))
        end = int(ref.findtext(ns+'end'))
        place_segments.append((start,end))
    place_segments.sort()
    result = ""
    i = 0
    for (start,end) in place_segments:
        result += text[i:start]
        result += "<u><b>"+text[start:end]+"</b></u>"
        i = end
    result += text[i:]
    return result

if __name__ == "__main__":
    print geoparsing(u"How long does it take to fly from San Francisco to Shanghai, China?")
