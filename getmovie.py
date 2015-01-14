#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json

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
    XML = XML.getroot()

    return XML

"""
HTML Datei erzeugen
"""
def htmlausgabe(data):
    datei = open("/Users/manuel/Desktop/Filmliste.html", "w")

    # Kopf schreiben
    datei.write("""
          <html>
          <head>
          <meta http-equiv="content-type" content="text/html; charset=utf-8">
          <title>Filmliste</title>
          <style type="text/css">
            table { width:100%; table-layout:fixed; }
            td { border:1px solid #000; vertical-align:top; overflow:hidden; }
          </style>
          </head>
             <body>\n
      """)

    #Inhalt schreiben
    datei.write("""
            <table>
                <tr>
                    <td colspan='5' style='width:100%'>Filmliste</td>
                </tr>
            </table>
            <table>
                <tr>
                    <td style='width:20px'>Nr</td>
                    <td style='width:150px'>Poster</td>
                    <td style='width:300px'>Titel/Datum</td>
                    <td style='width:80px'>Meta</td>
                    <td>Beschreibung</td>
                </tr>
        \n""")

    # the Data c, poster, title, datum, text, genre, resolution, channels
    for i in data:
        datei.write("<tr bgcolor='#CCCCCC'>")

        for inhalt in i:
            if inhalt and not type(inhalt) is int:
                try:
                    inhalt = unicode(inhalt, 'UTF-8')
                except:
                    inhalt = inhalt.encode('UTF-8')
            else:
                inhalt = str(inhalt)

            datei.write("<td valign='top'>" + inhalt + "</td>")

        datei.write("</tr>")

    datei.write("</table>\n")

    # Fuss schreiben
    datei.write(" </body> </html>\n")

    datei.close()

def getImages(title):
    headers = {
      'Accept': 'application/json'
    }

    # URL Quote
    title = urllib2.quote(title)

    # Film Poster holen
    request = urllib2.Request('http://api.themoviedb.org/3/search/movie?api_key=0dd32eece72fc9640fafaa5c87017fcf&language=de&query=' + title, headers=headers)
    response = urllib2.urlopen(request)
    data = json.load(response)

    try:
        return "<img src='http://image.tmdb.org/t/p/original" + data["results"][0]["poster_path"] + "' width='150'>"
    except:
        return "-"



filme = getXMLFromPMS(PlexServer)

data = []
c = 0
for filmname in filme.findall("Video"):
    c += 1
    zaehler = c
    poster = getImages(filmname.get("title").encode('UTF-8').replace("3D", ""))
    #poster = "bild"
    title = filmname.get("title")
    if filmname.get("originallyAvailableAt"):
        datum = filmname.get("originallyAvailableAt")
    else:
        datum = "-"
    text = filmname.get("summary")

    genre = ""
    for filmgenre in filmname.findall("Genre"):
        if genre != "":
            genre += ", " + filmgenre.get("tag")
        else:
            genre = filmgenre.get("tag")

    for filmid in filmname.findall("Media"):
        resolution = filmid.get("videoResolution") + "p"
        channels = filmid.get("audioChannels") + " Kanal"

    title_date = "<font size='5pt'><b>" + title + "</b></font><br><br>" + datum
    meta = genre + "<br><br>" + resolution + "<br>" + channels
    data.append([c, poster, title_date, meta, text])

htmlausgabe(data)