#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Das ist mein erstes kleines Python Programm. Es ist eigentlich mehr eine Übung.
Das Programm dient dazu die Filme von Plex auszulesen und als HTML Datei zu speichern.
"""

#### Konfiguration Start
PlexServer = "http://192.168.1.10:32400" # Server IP : Port
safe_to_path = "/Users/manuel/Desktop/" # Pfad wohin die HTML Datei geschrieben werden soll
#### Konfiguration Ende

#http://192.168.1.10:32400/library/sections/7/all
#addedAt
#viewCount

import urllib2
import json
from time import localtime, strftime, gmtime

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

# Plex Pfad und APIs
PlexServer = PlexServer + "/library/sections/7/all"
TMDB_api_key = "0bb5e601a83a20c54f09fbc45c6547f4" # API Key für TMDB
YOUTUBE_api_key = "AIzaSyBJdNrC3YAFJQbKpktxAWiYYwRdkMHVEXU" # API Key für Youtube

"""
XML Filmliste von Plex holen
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
    global safe_to_path

    jahr, monat, tag, stunde, minute = localtime()[0:5]
    gen_time = "%02i.%02i.%04i / %02i:%02i" % (tag,monat,jahr,stunde,minute)

    datei = open(safe_to_path + "Filmliste.html", "w")

    # Header schreiben
    datei.write("""
        <!--
        Achtung: Du musst die Datei erst herunter laden und dann im Browser (Safari, Firefox, IE) öffnen!
        -->

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

    #Tabellen Kopf schreiben
    datei.write("""
            <table>
                <tr>
                    <td colspan='3' style='width:80%; text-align:center; font-size:25pt;'>Filmliste</td>
                    <td style='text-align:right;'>Generiert: """ + gen_time + """</td>
                </tr>
            </table>
            <table>
                <tr>
                    <td style='width:150px; font-size:15pt;'>Poster</td>
                    <td style='width:300px; font-size:15pt;'>Titel/Datum</td>
                    <td style='width:80px; font-size:15pt;'>Meta</td>
                    <td style='font-size:15pt;'>Beschreibung</td>
                </tr>
        \n""")

    # the Data addDate, watched, poster, title_date, meta, text
    # Inhalte schreiben
    data.sort(reverse=True)
    c = 0
    for i in data:
        # Sort Datum löschen
        i.pop(0)

        # alternierende Zeilenfarbe
        if i.pop(0) == 0:
            if c == 0:
                c += 1
                datei.write("<tr bgcolor='#FFFFFF'>")
            else:
                c = 0
                datei.write("<tr bgcolor='#CCCCCC'>")
        else:
            datei.write("<tr bgcolor='red'>")

        # Inhalte ausgeben
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

"""
Links der Filmposter von TMDB holen
"""
def getImages(title):
    global TMDB_api_key

    # Leer und Sonderzeichen von String entfernen / URL Quote
    title = urllib2.quote(title)

    # Film Poster holen
    headers = {'Accept': 'application/json'}
    request = urllib2.Request('http://api.themoviedb.org/3/search/movie?api_key=' + TMDB_api_key + '&language=de&query=' + title, headers=headers)
    response = urllib2.urlopen(request)
    data = json.load(response)

    try:
        return "<img src='http://image.tmdb.org/t/p/original" + data["results"][0]["poster_path"] + "' width='150'>"
    except:
        return "-"

"""
Links zu Trailern von Youtube holen
"""
def getTrailer(title, jahr):
    global YOUTUBE_api_key

    # Leer und Sonderzeichen von String entfernen / URL Quote
    title = urllib2.quote("Film " + title + " " + jahr + " Trailer Deutsch German")

    # Film Trailer holen
    headers = {'Accept': 'application/json'}
    request = urllib2.Request("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&order=relevance&key=" + YOUTUBE_api_key + "&q=" + title, headers=headers)
    response = urllib2.urlopen(request)
    data = json.load(response)

    try:
        return "<a href='https://www.youtube.com/watch?v=" + data["items"][0]["id"]["videoId"] + "' target='_blank'>Movie Trailer</a>"
    except:
        return "-"



# Alle Filme von Plex holen
filme = getXMLFromPMS(PlexServer)

# XML von Plex aufsplitten und gebrauchte Infos holen
data = []
for filmname in filme.findall("Video"):

    # Film hinzugefügt
    sortDate = filmname.get("addedAt")
    addDate = strftime("%d.%m.%Y", gmtime(float(sortDate)))

    # Filmname
    title = filmname.get("title")

    # Erscheinungsjahr
    if filmname.get("year"):
        jahr = filmname.get("year") #filmname.get("originallyAvailableAt")[0:4]
    else:
        jahr = "-"

    # gesehen
    if filmname.get("viewCount"):
        watched = 1
    else:
        watched = 0

    text = filmname.get("summary")
    poster = getImages(filmname.get("title").encode('UTF-8').replace("3D", ""))
    #poster = "bild"
    trailer = getTrailer(filmname.get("title").encode('UTF-8').replace("(3D)", ""), jahr)
    #trailer = "trailer"

    genre = ""
    for filmgenre in filmname.findall("Genre"):
        if genre != "":
            genre += ", " + filmgenre.get("tag")
        else:
            genre = filmgenre.get("tag")

    for filmid in filmname.findall("Media"):
        resolution = filmid.get("videoResolution") + "p"
        channels = filmid.get("audioChannels") + " Kanal"

    title_date = "<font style='font-size:15pt;'><b>" + title + "</b></font><br><br>Erschienen: <b>" + jahr + "</b><br>Trailer: " + trailer + "<br><br>hinzugef&uuml;gt: " + addDate
    meta = genre + "<br><br>" + resolution + "<br>" + channels
    data.append([sortDate, watched, poster, title_date, meta, text])

# HTML Datei mit geholten Daten erzeugen
htmlausgabe(data)