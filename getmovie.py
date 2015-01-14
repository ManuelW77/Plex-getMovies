#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

PlexServer = "http://192.168.1.10:32400/library/sections/7/all"

"""
XML von Plex holen
"""
def getXMLFromPMS(URL):
    request = urllib2.Request(URL , None)
    response = urllib2.urlopen(request, timeout=20)
    XML = etree.parse(response)

    return XML

inhalt = getXMLFromPMS(PlexServer)
root = inhalt.getroot()

c = 0
for filmname in root.findall("Video"):
    c += 1
    print "{0:4d}".format(c), filmname.get('title')

